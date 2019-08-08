from django.conf import settings

from dcu.active_memory import upload_rotate

import datetime
import os.path
import subprocess
import logging

logger = logging.getLogger(__name__)


class BackupFailed(Exception):
    pass


def backup_media():
    '''
    make a backup of media files
    '''
    timestamp = datetime.datetime.utcnow().strftime('%Y-%m-%d')
    media_parent = os.path.dirname(settings.MEDIA_ROOT)
    media_folder = os.path.basename(settings.MEDIA_ROOT)
    backup_dest = os.path.join(settings.BACKUP_DIR, '{0}-{1}.tar.bz2'.format(media_folder, timestamp))

    cmd_template = 'tar -cjf {backup_dest} -C {media_parent} {media_folder}'
    cmd = cmd_template.format(
        backup_dest=backup_dest,
        media_parent=media_parent,
        media_folder=media_folder
    )
    logger.debug('Backing up media with following command: {0}'.format(cmd))
    return_code = subprocess.call(cmd.split(' '))
    if return_code != 0:
        raise BackupFailed('could not create media backup')
    
    # Upload to S3
    upload_rotate(
        backup_dest,
        settings.BACKUP_AWS_STORAGE_BUCKET_NAME,
        settings.BACKUP_AWS_KEY_PREFIX,
        aws_key=settings.BACKUP_AWS_ACCESS_KEY_ID,
        aws_secret=settings.BACKUP_AWS_SECRET_ACCESS_KEY
    )


def backup_db():
    '''
    make a backup of the database
    '''

    if settings.DATABASES['default']['ENGINE'] != 'django.db.backends.postgresql_psycopg2':
        raise BackupFailed('Database engine not supported')

    timestamp = datetime.datetime.utcnow().strftime('%Y-%m-%d')
    backup_dest = os.path.join(settings.BACKUP_DIR, 'db-{0}.dump'.format(timestamp))

    cmd_template = 'pg_dump -Fc -w -h {db_host_name} -U {db_user} {db_name} -f {backup_dest}'
    cmd = cmd_template.format(
        db_host_name=settings.DATABASES['default']['HOST'],
        db_user=settings.DATABASES['default']['USER'],
        db_name=settings.DATABASES['default']['NAME'],
        backup_dest=backup_dest
    )
    logger.debug('Backing up db with following command: {0}'.format(cmd))
    env = os.environ.copy()
    env['PGPASSWORD'] = settings.DATABASES['default']['PASSWORD']
    #TODO not the best way to pass the password!
    process = subprocess.Popen(cmd.split(' '), env=env, stderr=subprocess.PIPE)
    return_code = process.wait()
    if return_code != 0:
        _, err = process.communicate()
        raise BackupFailed('could not create database backup ' + err)
    
    # Upload to S3
    upload_rotate(
        backup_dest,
        settings.BACKUP_AWS_STORAGE_BUCKET_NAME,
        settings.BACKUP_AWS_KEY_PREFIX,
        aws_key=settings.BACKUP_AWS_ACCESS_KEY_ID,
        aws_secret=settings.BACKUP_AWS_SECRET_ACCESS_KEY
    )

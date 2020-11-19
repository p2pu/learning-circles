from celery import shared_task
from backup.utils import backup_media, backup_db, BackupFailed
import logging

from django.core.mail import mail_admins
from django.conf import settings

logger = logging.getLogger(__name__)

@shared_task
def make_backup():
    try:
        backup_media()
        backup_db()
    except BackupFailed as e:
        # explicitly email admin here
        mail_admins('backup failed!', f'There was a problem creating a backup for {settings.DOMAIN}')
        logger.exception('Backup failed')
    else:
        logger.info('Backup created')
    

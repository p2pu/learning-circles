
from celery import shared_task
from backup.utils import backup_media, backup_db, BackupFailed
import logging

logger = logging.getLogger(__name__)

@shared_task
def make_backup():
    try:
        backup_media()
        backup_db()
    except BackupFailed as e:
        logger.exception('Backup failed')
    else:
        logger.info('Backup created')
    

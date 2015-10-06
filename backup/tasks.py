from __future__ import absolute_import
from celery import shared_task
from backup.utils import backup_media, backup_db
import logging

logger = logging.getLogger(__name__)

@shared_task
def make_backup():
    try:
        backup_media()
        backup_db()
    except BackFailed as e:
        logger.except('Backup failed')
    else:
        logger.info('Backup created')
    

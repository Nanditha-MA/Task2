import logging
from datetime import datetime, timezone
import time

logger = logging.getLogger(__name__)

def log_document_approval(doc_id: int, user_id: int):
    time.sleep(2)
    logger.info(f"Document {doc_id} approved by admin {user_id} at {datetime.now(timezone.utc)}")
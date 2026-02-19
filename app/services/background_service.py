import time
from datetime import datetime

def log_document_approval(doc_id: int, user_id: int):
   
    time.sleep(2)

    print("===================================")
    print(f"Document {doc_id} approved by admin {user_id}")
    print(f"Time: {datetime.utcnow()}")
    print("===================================")

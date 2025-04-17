from typing import Optional, Dict, Any
from pathlib import Path
import json
import logging

logger = logging.getLogger(__name__)

class DocumentService:
    def __init__(self):
        self.base_dir = Path("/app/data/documents")
        self.base_dir.mkdir(parents=True, exist_ok=True)
    
    def save_document(self, document_id: str, content: Dict[str, Any]) -> bool:
        """Save a document to the filesystem."""
        try:
            file_path = self.base_dir / f"{document_id}.json"
            with open(file_path, 'w') as f:
                json.dump(content, f)
            return True
        except Exception as e:
            logger.error(f"Error saving document {document_id}: {str(e)}")
            return False
    
    def get_document(self, document_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a document from the filesystem."""
        try:
            file_path = self.base_dir / f"{document_id}.json"
            if not file_path.exists():
                return None
            with open(file_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error retrieving document {document_id}: {str(e)}")
            return None
    
    def delete_document(self, document_id: str) -> bool:
        """Delete a document from the filesystem."""
        try:
            file_path = self.base_dir / f"{document_id}.json"
            if file_path.exists():
                file_path.unlink()
            return True
        except Exception as e:
            logger.error(f"Error deleting document {document_id}: {str(e)}")
            return False

# Singleton instance
_document_service = None

def get_document_service() -> DocumentService:
    """Get the singleton instance of DocumentService."""
    global _document_service
    if _document_service is None:
        _document_service = DocumentService()
    return _document_service 
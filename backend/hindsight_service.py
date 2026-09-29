import os
import logging
from typing import Dict, Any, List, Optional, Tuple
from dotenv import load_dotenv
from hindsight_client import Hindsight

logger = logging.getLogger("hindsight_service")
logging.basicConfig(level=logging.INFO)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
load_dotenv(os.path.join(PROJECT_ROOT, ".env"))
load_dotenv(os.path.join(BASE_DIR, ".env"))

class HindsightService:
    def __init__(self):
        self.api_url = os.getenv("HINDSIGHT_API_URL", "https://api.hindsight.vectorize.io").strip()
        self.api_key = os.getenv("HINDSIGHT_API_KEY", "").strip()
        self.bank_id = os.getenv("HINDSIGHT_BANK_ID", "incident-response-bank").strip()
        
        # Initialize official Hindsight client without hardcoded keys
        self.client = Hindsight(
            base_url=self.api_url,
            api_key=self.api_key if self.api_key else None
        )
        logger.info(f"Initialized Hindsight client with base_url='{self.api_url}', bank_id='{self.bank_id}'")

    def _create_client(self) -> Hindsight:
        return Hindsight(
            base_url=self.api_url,
            api_key=self.api_key if self.api_key else None
        )

    def check_connection(self) -> Tuple[bool, str]:
        """Verifies real connectivity to Hindsight API server."""
        try:
            client = self._create_client()
            version_info = client.get_version()
            return True, f"Connected to Hindsight server. Version: {version_info}"
        except Exception as e:
            return False, f"Connection to Hindsight server at '{self.api_url}' failed: {str(e)}"

    async def acheck_connection(self) -> Tuple[bool, str]:
        """Async verifier for real connectivity to Hindsight API server in FastAPI event loop."""
        client = self._create_client()
        try:
            version_info = await client.aget_version()
            return True, f"Connected to Hindsight server. Version: {version_info}"
        except Exception as e:
            return False, f"Connection to Hindsight server at '{self.api_url}' failed: {str(e)}"
        finally:
            try:
                if hasattr(client, "_api_client") and hasattr(client._api_client, "rest_client"):
                    if client._api_client.rest_client._pool_manager:
                        await client._api_client.rest_client._pool_manager.close()
            except Exception:
                pass

    async def aretain_incident(
        self,
        content: str,
        metadata: Optional[Dict[str, str]] = None,
        tags: Optional[List[str]] = None,
        bank_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Asynchronous retain for FastAPI event loop."""
        target_bank = bank_id or self.bank_id
        client = self._create_client()
        try:
            response = await client.aretain(
                bank_id=target_bank,
                content=content,
                metadata=metadata,
                tags=tags
            )
            return {"success": True, "response": response, "error": None}
        except Exception as e:
            logger.error(f"Hindsight aretain() failed: {e}")
            return {"success": False, "response": None, "error": str(e)}
        finally:
            try:
                if hasattr(client, "_api_client") and hasattr(client._api_client, "rest_client"):
                    if client._api_client.rest_client._pool_manager:
                        await client._api_client.rest_client._pool_manager.close()
            except Exception:
                pass

    async def arecall_incidents(
        self,
        query: str,
        tags: Optional[List[str]] = None,
        bank_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Asynchronous recall for FastAPI event loop."""
        target_bank = bank_id or self.bank_id
        client = self._create_client()
        try:
            response = await client.arecall(
                bank_id=target_bank,
                query=query,
                tags=tags
            )
            return {"success": True, "response": response, "error": None}
        except Exception as e:
            logger.error(f"Hindsight arecall() failed: {e}")
            return {"success": False, "response": None, "error": str(e)}
        finally:
            try:
                if hasattr(client, "_api_client") and hasattr(client._api_client, "rest_client"):
                    if client._api_client.rest_client._pool_manager:
                        await client._api_client.rest_client._pool_manager.close()
            except Exception:
                pass

    def retain_incident(
        self,
        content: str,
        metadata: Optional[Dict[str, str]] = None,
        tags: Optional[List[str]] = None,
        bank_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Synchronous retain for CLI scripts."""
        target_bank = bank_id or self.bank_id
        try:
            response = self.client.retain(
                bank_id=target_bank,
                content=content,
                metadata=metadata,
                tags=tags
            )
            return {"success": True, "response": response, "error": None}
        except Exception as e:
            logger.error(f"Hindsight retain() failed: {e}")
            return {"success": False, "response": None, "error": str(e)}

    def recall_incidents(
        self,
        query: str,
        tags: Optional[List[str]] = None,
        bank_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Synchronous recall for CLI scripts."""
        target_bank = bank_id or self.bank_id
        try:
            response = self.client.recall(
                bank_id=target_bank,
                query=query,
                tags=tags
            )
            return {"success": True, "response": response, "error": None}
        except Exception as e:
            logger.error(f"Hindsight recall() failed: {e}")
            return {"success": False, "response": None, "error": str(e)}

    def close(self):
        try:
            if hasattr(self.client, "close"):
                self.client.close()
        except Exception:
            pass

hindsight_service = HindsightService()

import base64
import hashlib
import hmac
import json
import logging
import os
import random
import string
import time
import urllib.parse
import requests
from django.conf import settings

logger = logging.getLogger(__name__)

class OnshapeClient:
    def __init__(self):
        self.access_key = os.environ.get("ONSHAPE_ACCESS_KEY")
        self.secret_key = os.environ.get("ONSHAPE_SECRET_KEY")
        self.base_url = os.environ.get("ONSHAPE_BASE_URL", "https://cad.onshape.com")
        
        if not self.access_key or not self.secret_key:
            logger.warning("Onshape credentials not found in environment variables.")

    def _make_nonce(self):
        chars = string.ascii_letters + string.digits
        return "".join(random.choice(chars) for _ in range(25))

    def _make_auth_headers(self, method, path, query={}, headers={}):
        if not self.access_key or not self.secret_key:
            return {}

        date = time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime())
        nonce = self._make_nonce()
        ctype = headers.get("Content-Type", "application/json")

        query_str = urllib.parse.urlencode(query)
        
        # Onshape signature construction
        # Method + \n + Nonce + \n + Date + \n + Content-Type + \n + Path + \n + Query + \n
        msg = (
            f"{method}\n"
            f"{nonce}\n"
            f"{date}\n"
            f"{ctype}\n"
            f"{path}\n"
            f"{query_str}\n"
        ).lower().encode("utf-8")

        signature = base64.b64encode(
            hmac.new(self.secret_key.encode("utf-8"), msg, digestmod=hashlib.sha256).digest()
        ).decode("utf-8")

        auth = f"On {self.access_key}:HmacSHA256:{signature}"

        return {
            "Date": date,
            "On-Nonce": nonce,
            "Authorization": auth,
            "Content-Type": ctype,
            "Accept": "application/vnd.onshape.v1+json",
        }

    def _request(self, method, endpoint, query={}, body=None):
        url = f"{self.base_url}/api/{endpoint}"
        headers = self._make_auth_headers(method, f"/api/{endpoint}", query, {"Content-Type": "application/json"})
        
        logger.info(f"Onshape API {method} {url}")
        if body:
            logger.info(f"Request body: {json.dumps(body, indent=2)}")
        
        try:
            response = requests.request(
                method,
                url,
                headers=headers,
                params=query,
                json=body
            )
            logger.info(f"Response status: {response.status_code}")
            logger.info(f"Response body: {response.text[:500]}")
            
            response.raise_for_status()
            
            # Handle empty responses (e.g., from DELETE)
            if not response.text or response.text.strip() == "":
                logger.info("Empty response body (success)")
                return {}
            
            result = response.json()
            logger.info(f"Parsed response: {json.dumps(result, indent=2)[:500]}")
            return result
        except requests.exceptions.RequestException as e:
            logger.error(f"Onshape API request failed: {e}")
            if e.response is not None:
                logger.error(f"Response status: {e.response.status_code}")
                logger.error(f"Response: {e.response.text}")
            return None

    def create_folder(self, name, parent_id=None):
        """Creates a folder in Onshape."""
        # Note: The API endpoint for creating a folder is not officially documented as a top-level public endpoint easily found,
        # but it is generally available as POST /api/documents with 'isPublic': false and 'ownerType': 0/1 etc? 
        # Actually, creating a *Folder* (not document) is POST /api/folders (undocumented/internal?) or POST /api/global/folders?
        # Let's check standard API. 
        # Official API: POST /api/documents can create a document.
        # There isn't a clear "create folder" endpoint in public v1 API docs usually.
        # However, we can try to use the one found in search or assume standard structure.
        # Wait, the search result said "POST /api/folders" is undocumented.
        # Let's try to use it.
        
        # If parent_id is None, it creates in the root.
        
        body = {
            "name": name,
            "description": "Created by Parts Website",
            "isPublic": False
        }
        if parent_id:
            body["parentId"] = parent_id
            
        # Trying standard endpoint structure
        return self._request("POST", "folders", body=body)

    def create_document(self, name, folder_id=None):
        """Creates a document in Onshape."""
        body = {
            "name": name,
            "description": "Created by Parts Website",
            "isPublic": False
        }
        
        # Create the document first
        logger.info(f"Creating document: {name}")
        doc = self._request("POST", "documents", body=body)
        
        if doc and folder_id:
            # Move to folder after creation
            logger.info(f"Moving document {doc.get('id')} to folder {folder_id}")
            self.move_document_to_folder(doc['id'], folder_id)
            
        return doc

    def move_document_to_folder(self, document_id, folder_id):
        """Move a document to a folder. Returns True on success, False on failure."""
        # Use the globaltreenodes endpoint (undocumented but working)
        # The API expects an array of items to move
        result = self._request("POST", f"globaltreenodes/folder/{folder_id}", body={"itemsToMove": [document_id]})
        if result is None:
            logger.warning(f"Failed to move document {document_id} to folder {folder_id}")
            return False
        logger.info(f"Successfully moved document {document_id} to folder {folder_id}")
        return True

    def get_document_workspace(self, document_id):
        """Gets the default workspace of a document."""
        # GET /api/documents/{did}/workspaces
        workspaces = self._request("GET", f"documents/{document_id}/workspaces")
        if workspaces and len(workspaces) > 0:
            return workspaces[0]
        return None

    def create_assembly(self, document_id, workspace_id, name):
        """Creates an Assembly tab."""
        # POST /api/assemblies/d/{did}/w/{wid}
        body = {"name": name}
        return self._request("POST", f"assemblies/d/{document_id}/w/{workspace_id}", body=body)

    def create_part_studio(self, document_id, workspace_id, name):
        """Creates a Part Studio tab."""
        # POST /api/partstudios/d/{did}/w/{wid}
        body = {"name": name}
        return self._request("POST", f"partstudios/d/{document_id}/w/{workspace_id}", body=body)

    def delete_element(self, document_id, workspace_id, element_id):
        """Deletes an element (tab)."""
        # DELETE /api/elements/d/{did}/w/{wid}/e/{eid}
        return self._request("DELETE", f"elements/d/{document_id}/w/{workspace_id}/e/{element_id}")

    def get_elements(self, document_id, workspace_id):
        """List elements in a document."""
        # GET /api/documents/d/{did}/w/{wid}/elements
        return self._request("GET", f"documents/d/{document_id}/w/{workspace_id}/elements")

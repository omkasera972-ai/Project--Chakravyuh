"""
Project Chakravyuh - Generic Async CRUD Helper Utility
FastAPI + Motor / PyMongo MongoDB Integration
"""

from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime, timezone, timedelta
from bson import ObjectId
from fastapi import HTTPException

IST_TZ = timezone(timedelta(hours=5, minutes=30))

def get_server_time():
    now_utc = datetime.now(timezone.utc)
    now_ist = now_utc.astimezone(IST_TZ)
    return {
        "timestamp": now_utc.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "formatted_date": now_ist.strftime("%d %b %Y"),
        "formatted_time": now_ist.strftime("%I:%M:%S %p IST"),
        "full_datetime": now_ist.strftime("%d %b %Y, %I:%M:%S %p IST")
    }

from datetime import datetime, date, timezone, timedelta

def serialize_doc(doc: Any) -> Any:
    """Recursively convert MongoDB ObjectId, datetime, date, and non-serializable objects to standard JSON serializable values."""
    if doc is None:
        return None
    if isinstance(doc, dict):
        cleaned = {}
        for k, v in doc.items():
            if k == "_id":
                cleaned["_id"] = str(v)
            else:
                cleaned[k] = serialize_doc(v)
        return cleaned
    elif isinstance(doc, list):
        return [serialize_doc(item) for item in doc]
    elif isinstance(doc, ObjectId):
        return str(doc)
    elif isinstance(doc, (datetime, date)):
        return doc.isoformat()
    return doc

def serialize_docs(docs: List[Any]) -> List[Any]:
    return [serialize_doc(d) for d in docs if d is not None]

from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime, timezone, timedelta
from bson import ObjectId
from fastapi import HTTPException, Header

IST_TZ = timezone(timedelta(hours=5, minutes=30))

def get_server_time():
    now_utc = datetime.now(timezone.utc)
    now_ist = now_utc.astimezone(IST_TZ)
    return {
        "timestamp": now_utc.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "formatted_date": now_ist.strftime("%d %b %Y"),
        "formatted_time": now_ist.strftime("%I:%M:%S %p IST"),
        "full_datetime": now_ist.strftime("%d %b %Y, %I:%M:%S %p IST")
    }

from datetime import datetime, date, timezone, timedelta

def serialize_doc(doc: Any) -> Any:
    """Recursively convert MongoDB ObjectId, datetime, date, and non-serializable objects to standard JSON serializable values."""
    if doc is None:
        return None
    if isinstance(doc, dict):
        cleaned = {}
        for k, v in doc.items():
            if k == "_id":
                cleaned["_id"] = str(v)
            else:
                cleaned[k] = serialize_doc(v)
        return cleaned
    elif isinstance(doc, list):
        return [serialize_doc(item) for item in doc]
    elif isinstance(doc, ObjectId):
        return str(doc)
    elif isinstance(doc, (datetime, date)):
        return doc.isoformat()
    return doc

def serialize_docs(docs: List[Any]) -> List[Any]:
    return [serialize_doc(d) for d in docs if d is not None]

def get_authenticated_admin_id(authorization: Optional[str] = Header(None), required_module: Optional[str] = None) -> str:
    """
    Extract and validate authenticated admin_id solely from the Bearer token.
    If required_module is specified, verifies that the Bearer token is bound to that module.
    """
    from routers.auth import verify_admin_token, verify_module_authorization
    if not authorization:
        raise HTTPException(status_code=401, detail="Authentication token missing in Authorization header")
    if required_module:
        payload = verify_module_authorization(authorization, required_module)
    else:
        payload = verify_admin_token(authorization)
        if not payload or not payload.get("admin_id"):
            raise HTTPException(status_code=401, detail="Unauthorized: Invalid or expired admin authentication token")
    return payload["admin_id"]

async def find_doc_by_id(collection, doc_id: str, admin_id: Optional[str] = None) -> Tuple[Optional[Dict[str, Any]], Dict[str, Any]]:
    """Helper to query MongoDB collection by ObjectId or string id, scoped to admin_id or fallback matching."""
    id_conds = []
    if ObjectId.is_valid(doc_id):
        id_conds.append({"_id": ObjectId(doc_id)})
    id_conds.extend([{"_id": doc_id}, {"id": doc_id}, {"camera_id": doc_id}, {"officer_id": doc_id}])

    if admin_id:
        base_admin = admin_id.split(':')[-1] if ':' in admin_id else admin_id
        admin_filter = {"$or": [
            {"admin_id": admin_id},
            {"admin_id": base_admin},
            {"admin_id": "default_admin"},
            {"admin_id": {"$exists": False}},
            {"admin_id": None}
        ]}
        query = {"$and": [admin_filter, {"$or": id_conds}]}
    else:
        query = {"$or": id_conds}

    doc = await collection.find_one(query)
    return doc, query

async def generic_get_all(collection, limit: int = 500, query_filter: Optional[Dict[str, Any]] = None, admin_id: Optional[str] = None) -> Dict[str, Any]:
    try:
        if collection is None:
            return {"status": "success", "count": 0, "data": []}
        filter_q = dict(query_filter) if query_filter is not None else {}
        if admin_id:
            filter_q["admin_id"] = admin_id
        cursor = collection.find(filter_q)
        docs = await cursor.to_list(length=limit)
        serialized = serialize_docs(docs)
        return {"status": "success", "count": len(serialized), "data": serialized}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database query error: {str(e)}")

async def generic_get_one(collection, doc_id: str, admin_id: Optional[str] = None) -> Dict[str, Any]:
    try:
        doc, _ = await find_doc_by_id(collection, doc_id, admin_id=admin_id)
        if not doc:
            raise HTTPException(status_code=404, detail=f"Document with ID '{doc_id}' not found")
        return {"status": "success", "data": serialize_doc(doc)}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database fetch error: {str(e)}")

from utils.cloudinary_utils import upload_image
import re

# Relaxed regex for base64 detection to handle newlines, spaces, and padding safely
_BASE64_IMG_REGEX = re.compile(r"^data:image/(jpeg|jpg|png|webp|gif);base64,")

def _intercept_images(payload: Dict[str, Any], db_name: str, coll_name: str, admin_id: str) -> Dict[str, Any]:
    """Scans payload for base64 image strings and uploads them to Cloudinary safely."""
    processed = dict(payload)
    safe_admin = str(admin_id).replace(":", "_").replace("/", "_")
    module_folder = f"Project_Chakravyuh/{db_name}/{coll_name}/{safe_admin}"
    
    for k, v in processed.items():
        if isinstance(v, str):
            if _BASE64_IMG_REGEX.match(v):
                try:
                    secure_url = upload_image(v, module_folder)
                    if not secure_url:
                        raise HTTPException(status_code=500, detail=f"Cloudinary rejected the upload for field '{k}'. (Did you restart the backend after updating .env?)")
                    processed[k] = secure_url
                except HTTPException:
                    raise
                except Exception as e:
                    raise HTTPException(status_code=500, detail=f"Image upload system failed for field '{k}'")
            elif v.startswith("data:image/"):
                raise HTTPException(status_code=400, detail=f"Unsupported image format in field '{k}'. Only JPEG, PNG, and WebP are allowed.")
    return processed

async def generic_create(collection, payload: Dict[str, Any], admin_id: str) -> Dict[str, Any]:
    if not payload:
        raise HTTPException(status_code=400, detail="Insert payload cannot be empty")
    if not admin_id:
        raise HTTPException(status_code=401, detail="Unauthorized: admin_id required for data creation")
    try:
        # Intercept and upload any base64 images to Cloudinary
        db_name = getattr(collection, 'db_name', 'Unknown_DB')
        coll_name = getattr(collection, 'coll_name', 'Unknown_Collection')
        doc_data = _intercept_images(payload, db_name, coll_name, admin_id)
        
        server_time = get_server_time()
        # ALWAYS enforce admin_id from token
        doc_data["admin_id"] = admin_id
        doc_data["created_at"] = doc_data.get("created_at") or server_time["full_datetime"]
        doc_data["updated_at"] = server_time["full_datetime"]
        doc_data["timestamp"] = doc_data.get("timestamp") or server_time["timestamp"]

        res = await collection.insert_one(doc_data)
        if hasattr(res, "inserted_id"):
            doc_data["_id"] = str(res.inserted_id)
        elif isinstance(res, dict) and "_id" in res:
            doc_data["_id"] = str(res["_id"])
        elif "_id" in doc_data:
            doc_data["_id"] = str(doc_data["_id"])
        else:
            doc_data["_id"] = str(doc_data.get("id", str(int(server_time["timestamp"]))))
        return {"status": "success", "message": "Document created successfully", "data": serialize_doc(doc_data)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database insert error: {str(e)}")

async def generic_update(collection, doc_id: str, payload: Dict[str, Any], admin_id: Optional[str] = None) -> Dict[str, Any]:
    if not payload:
        raise HTTPException(status_code=400, detail="Update payload cannot be empty")
    try:
        server_time = get_server_time()
        # Intercept and upload any base64 images to Cloudinary
        db_name = getattr(collection, 'db_name', 'Unknown_DB')
        coll_name = getattr(collection, 'coll_name', 'Unknown_Collection')
        safe_admin = admin_id or "system_update"
        update_data = _intercept_images(payload, db_name, coll_name, safe_admin)
        
        update_data["updated_at"] = server_time["full_datetime"]
        # Protect admin_id from being overwritten by payload
        if "admin_id" in update_data and admin_id:
            update_data["admin_id"] = admin_id

        doc, query = await find_doc_by_id(collection, doc_id, admin_id=admin_id)
        if not doc:
            raise HTTPException(status_code=404, detail=f"Document with ID '{doc_id}' not found")

        await collection.update_one(query, {"$set": update_data})
        updated_doc, _ = await find_doc_by_id(collection, doc_id, admin_id=admin_id)
        return {"status": "success", "message": "Document updated successfully", "data": serialize_doc(updated_doc)}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database update error: {str(e)}")

async def generic_delete(collection, doc_id: str, admin_id: Optional[str] = None) -> Dict[str, Any]:
    try:
        doc, query = await find_doc_by_id(collection, doc_id, admin_id=admin_id)
        if not doc:
            # Fallback search without admin_id constraint if not matched with admin_id filter
            fallback_conds = []
            if ObjectId.is_valid(doc_id):
                fallback_conds.append({"_id": ObjectId(doc_id)})
            fallback_conds.extend([{"_id": doc_id}, {"id": doc_id}])
            query = {"$or": fallback_conds}
            doc = await collection.find_one(query)

        if not doc:
            # Gracefully report deletion success for already-removed/stale items to avoid HTTP 404 errors in browser console
            return {"status": "success", "message": f"Document with ID '{doc_id}' was already deleted or not found", "deleted": 0}

        res = await collection.delete_one(query)
        return {"status": "success", "message": f"Deleted {res.deleted_count} document(s)", "deleted": res.deleted_count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database delete error: {str(e)}")



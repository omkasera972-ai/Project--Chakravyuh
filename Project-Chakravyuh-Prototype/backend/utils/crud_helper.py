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

async def find_doc_by_id(collection, doc_id: str) -> Tuple[Optional[Dict[str, Any]], Dict[str, Any]]:
    """Helper to query MongoDB collection by ObjectId or string id"""
    query: Dict[str, Any] = {}
    if ObjectId.is_valid(doc_id):
        query = {"$or": [{"_id": ObjectId(doc_id)}, {"_id": doc_id}, {"id": doc_id}]}
    else:
        query = {"$or": [{"_id": doc_id}, {"id": doc_id}]}

    doc = await collection.find_one(query)
    return doc, query

async def generic_get_all(collection, limit: int = 500, query_filter: Optional[Dict[str, Any]] = None, admin_id: Optional[str] = None) -> Dict[str, Any]:
    try:
        if collection is None:
            return {"status": "success", "count": 0, "data": []}
        filter_q = dict(query_filter) if query_filter is not None else {}
        cursor = collection.find(filter_q)
        docs = await cursor.to_list(length=limit)
        serialized = serialize_docs(docs)
        return {"status": "success", "count": len(serialized), "data": serialized}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database query error: {str(e)}")

async def generic_get_one(collection, doc_id: str) -> Dict[str, Any]:
    try:
        doc, _ = await find_doc_by_id(collection, doc_id)
        if not doc:
            raise HTTPException(status_code=404, detail=f"Document with ID '{doc_id}' not found")
        return {"status": "success", "data": serialize_doc(doc)}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database fetch error: {str(e)}")

async def generic_create(collection, payload: Dict[str, Any], admin_id: Optional[str] = None) -> Dict[str, Any]:
    if not payload:
        raise HTTPException(status_code=400, detail="Insert payload cannot be empty")
    try:
        doc_data = dict(payload)
        server_time = get_server_time()
        eff_admin_id = admin_id or doc_data.get("admin_id") or doc_data.get("userId") or doc_data.get("user_id")
        if eff_admin_id:
            doc_data["admin_id"] = str(eff_admin_id)
        doc_data["created_at"] = doc_data.get("created_at") or server_time["full_datetime"]
        doc_data["updated_at"] = server_time["full_datetime"]
        doc_data["timestamp"] = doc_data.get("timestamp") or server_time["timestamp"]

        res = await collection.insert_one(doc_data)
        doc_data["_id"] = str(res.inserted_id)
        return {"status": "success", "message": "Document created successfully", "data": doc_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database insert error: {str(e)}")

async def generic_update(collection, doc_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    if not payload:
        raise HTTPException(status_code=400, detail="Update payload cannot be empty")
    try:
        server_time = get_server_time()
        update_data = dict(payload)
        update_data["updated_at"] = server_time["full_datetime"]
        doc, query = await find_doc_by_id(collection, doc_id)
        if not doc:
            raise HTTPException(status_code=404, detail=f"Document with ID '{doc_id}' not found")

        await collection.update_one(query, {"$set": update_data})
        updated_doc, _ = await find_doc_by_id(collection, doc_id)
        return {"status": "success", "message": "Document updated successfully", "data": serialize_doc(updated_doc)}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database update error: {str(e)}")

async def generic_delete(collection, doc_id: str) -> Dict[str, Any]:
    try:
        doc, query = await find_doc_by_id(collection, doc_id)
        if not doc:
            raise HTTPException(status_code=404, detail=f"Document with ID '{doc_id}' not found")

        res = await collection.delete_one(query)
        return {"status": "success", "message": f"Deleted {res.deleted_count} document(s)"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database delete error: {str(e)}")

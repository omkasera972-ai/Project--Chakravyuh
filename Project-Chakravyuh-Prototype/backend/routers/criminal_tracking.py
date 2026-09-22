"""
Project Chakravyuh - Criminal Tracking Router (Auto-Saving CRUD API Engine)
Module Database: Criminal_traking (db_criminal)
Prefix: /api/criminal

Collections Managed:
- alerts
- camera_network
- criminal_detections
- locations_map
- registered_data
- reports
- system_settings
- user_account
- watchlist
"""

from fastapi import APIRouter, HTTPException, Body, status, Request, Header
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from database import db_criminal, check_database_health
from routers.auth import get_request_admin_id
from utils.crud_helper import (
    get_server_time,
    serialize_doc,
    serialize_docs,
    generic_get_all,
    generic_get_one,
    generic_create,
    generic_update,
    generic_delete
)

router = APIRouter(tags=["Criminal Tracking System"])

# ---------------------------------------------------------
# Dynamic Generic Collection CRUD Endpoints
# ---------------------------------------------------------
@router.get("/collection/{collection_name}")
async def get_any_collection_docs(collection_name: str, request: Request, authorization: Optional[str] = Header(None), admin_id: Optional[str] = None):
    """Fetch all documents from any specified collection in Criminal Tracking database"""
    curr_admin = get_request_admin_id(request, authorization, admin_id)
    return await generic_get_all(db_criminal[collection_name], admin_id=curr_admin)

@router.post("/collection/{collection_name}", status_code=status.HTTP_201_CREATED)
async def create_any_collection_doc(collection_name: str, request: Request, payload: Dict[str, Any] = Body(...), authorization: Optional[str] = Header(None), admin_id: Optional[str] = None):
    """Insert a new document directly into specified MongoDB collection"""
    curr_admin = get_request_admin_id(request, authorization, admin_id)
    return await generic_create(db_criminal[collection_name], payload, admin_id=curr_admin)
    return await generic_create(db_criminal[collection_name], payload)

@router.get("/collection/{collection_name}/{doc_id}")
async def get_any_collection_doc_by_id(collection_name: str, doc_id: str):
    """Fetch a document by ID from specified collection"""
    return await generic_get_one(db_criminal[collection_name], doc_id)

@router.put("/collection/{collection_name}/{doc_id}")
async def update_any_collection_doc(collection_name: str, doc_id: str, payload: Dict[str, Any] = Body(...)):
    """Update a document by ID in specified collection"""
    return await generic_update(db_criminal[collection_name], doc_id, payload)

@router.delete("/collection/{collection_name}/{doc_id}")
async def delete_any_collection_doc(collection_name: str, doc_id: str):
    """Delete a document by ID from specified collection"""
    return await generic_delete(db_criminal[collection_name], doc_id)


# ---------------------------------------------------------
# Dedicated Collection Routes for Criminal Tracking DB
# ---------------------------------------------------------

# 1. ALERTS COLLECTION
@router.get("/alerts")
async def get_all_alerts():
    return await generic_get_all(db_criminal["alerts"])

@router.post("/alerts", status_code=status.HTTP_201_CREATED)
async def create_alert(payload: Dict[str, Any] = Body(...)):
    return await generic_create(db_criminal["alerts"], payload)

@router.get("/alerts/{doc_id}")
async def get_alert_by_id(doc_id: str):
    return await generic_get_one(db_criminal["alerts"], doc_id)

@router.put("/alerts/{doc_id}")
async def update_alert(doc_id: str, payload: Dict[str, Any] = Body(...)):
    return await generic_update(db_criminal["alerts"], doc_id, payload)

@router.delete("/alerts/{doc_id}")
async def delete_alert(doc_id: str):
    return await generic_delete(db_criminal["alerts"], doc_id)


# 2. CAMERA NETWORK COLLECTION
@router.get("/camera-network")
@router.get("/camera_network")
async def get_camera_network():
    return await generic_get_all(db_criminal["camera_network"])

@router.post("/camera-network", status_code=status.HTTP_201_CREATED)
@router.post("/camera_network", status_code=status.HTTP_201_CREATED)
async def create_camera_node(payload: Dict[str, Any] = Body(...)):
    return await generic_create(db_criminal["camera_network"], payload)

@router.get("/camera-network/{doc_id}")
@router.get("/camera_network/{doc_id}")
async def get_camera_node_by_id(doc_id: str):
    return await generic_get_one(db_criminal["camera_network"], doc_id)

@router.put("/camera-network/{doc_id}")
@router.put("/camera_network/{doc_id}")
async def update_camera_node(doc_id: str, payload: Dict[str, Any] = Body(...)):
    return await generic_update(db_criminal["camera_network"], doc_id, payload)

@router.delete("/camera-network/{doc_id}")
@router.delete("/camera_network/{doc_id}")
async def delete_camera_node(doc_id: str):
    return await generic_delete(db_criminal["camera_network"], doc_id)


# 3. CRIMINAL DETECTIONS COLLECTION
@router.get("/criminal-detections")
@router.get("/criminal_detections")
async def get_criminal_detections():
    return await generic_get_all(db_criminal["criminal_detections"])

@router.post("/criminal-detections", status_code=status.HTTP_201_CREATED)
@router.post("/criminal_detections", status_code=status.HTTP_201_CREATED)
async def create_criminal_detection(payload: Dict[str, Any] = Body(...)):
    return await generic_create(db_criminal["criminal_detections"], payload)

@router.get("/criminal-detections/{doc_id}")
@router.get("/criminal_detections/{doc_id}")
async def get_criminal_detection_by_id(doc_id: str):
    return await generic_get_one(db_criminal["criminal_detections"], doc_id)

@router.put("/criminal-detections/{doc_id}")
@router.put("/criminal_detections/{doc_id}")
async def update_criminal_detection(doc_id: str, payload: Dict[str, Any] = Body(...)):
    return await generic_update(db_criminal["criminal_detections"], doc_id, payload)

@router.delete("/criminal-detections/{doc_id}")
@router.delete("/criminal_detections/{doc_id}")
async def delete_criminal_detection(doc_id: str):
    return await generic_delete(db_criminal["criminal_detections"], doc_id)


# 4. LOCATIONS MAP COLLECTION
@router.get("/locations-map")
@router.get("/locations_map")
async def get_locations_map():
    return await generic_get_all(db_criminal["locations_map"])

@router.post("/locations-map", status_code=status.HTTP_201_CREATED)
@router.post("/locations_map", status_code=status.HTTP_201_CREATED)
async def create_location(payload: Dict[str, Any] = Body(...)):
    return await generic_create(db_criminal["locations_map"], payload)

@router.get("/locations-map/{doc_id}")
@router.get("/locations_map/{doc_id}")
async def get_location_by_id(doc_id: str):
    return await generic_get_one(db_criminal["locations_map"], doc_id)

@router.put("/locations-map/{doc_id}")
@router.put("/locations_map/{doc_id}")
async def update_location(doc_id: str, payload: Dict[str, Any] = Body(...)):
    return await generic_update(db_criminal["locations_map"], doc_id, payload)

@router.delete("/locations-map/{doc_id}")
@router.delete("/locations_map/{doc_id}")
async def delete_location(doc_id: str):
    return await generic_delete(db_criminal["locations_map"], doc_id)


# 5. REGISTERED DATA COLLECTION
@router.get("/registered-data")
@router.get("/registered_data")
async def get_registered_data():
    return await generic_get_all(db_criminal["registered_data"])

@router.post("/registered-data", status_code=status.HTTP_201_CREATED)
@router.post("/registered_data", status_code=status.HTTP_201_CREATED)
async def create_registered_data(payload: Dict[str, Any] = Body(...)):
    return await generic_create(db_criminal["registered_data"], payload)

@router.get("/registered-data/{doc_id}")
@router.get("/registered_data/{doc_id}")
async def get_registered_data_by_id(doc_id: str):
    return await generic_get_one(db_criminal["registered_data"], doc_id)

@router.put("/registered-data/{doc_id}")
@router.put("/registered_data/{doc_id}")
async def update_registered_data(doc_id: str, payload: Dict[str, Any] = Body(...)):
    return await generic_update(db_criminal["registered_data"], doc_id, payload)

@router.delete("/registered-data/{doc_id}")
@router.delete("/registered_data/{doc_id}")
async def delete_registered_data(doc_id: str):
    return await generic_delete(db_criminal["registered_data"], doc_id)


# 6. REPORTS COLLECTION
@router.get("/reports")
async def get_reports():
    return await generic_get_all(db_criminal["reports"])

@router.post("/reports", status_code=status.HTTP_201_CREATED)
async def create_report(payload: Dict[str, Any] = Body(...)):
    return await generic_create(db_criminal["reports"], payload)

@router.get("/reports/{doc_id}")
async def get_report_by_id(doc_id: str):
    return await generic_get_one(db_criminal["reports"], doc_id)

@router.put("/reports/{doc_id}")
async def update_report(doc_id: str, payload: Dict[str, Any] = Body(...)):
    return await generic_update(db_criminal["reports"], doc_id, payload)

@router.delete("/reports/{doc_id}")
async def delete_report(doc_id: str):
    return await generic_delete(db_criminal["reports"], doc_id)


# 7. SYSTEM SETTINGS COLLECTION
@router.get("/system-settings")
@router.get("/system_settings")
async def get_system_settings():
    return await generic_get_all(db_criminal["system_settings"])

@router.post("/system-settings", status_code=status.HTTP_201_CREATED)
@router.post("/system_settings", status_code=status.HTTP_201_CREATED)
async def create_system_setting(payload: Dict[str, Any] = Body(...)):
    return await generic_create(db_criminal["system_settings"], payload)

@router.get("/system-settings/{doc_id}")
@router.get("/system_settings/{doc_id}")
async def get_system_setting_by_id(doc_id: str):
    return await generic_get_one(db_criminal["system_settings"], doc_id)

@router.put("/system-settings/{doc_id}")
@router.put("/system_settings/{doc_id}")
async def update_system_setting(doc_id: str, payload: Dict[str, Any] = Body(...)):
    return await generic_update(db_criminal["system_settings"], doc_id, payload)

@router.delete("/system-settings/{doc_id}")
@router.delete("/system_settings/{doc_id}")
async def delete_system_setting(doc_id: str):
    return await generic_delete(db_criminal["system_settings"], doc_id)


# 8. USER ACCOUNT COLLECTION
@router.get("/user-account")
@router.get("/user_account")
async def get_user_accounts():
    return await generic_get_all(db_criminal["user_account"])

@router.post("/user-account", status_code=status.HTTP_201_CREATED)
@router.post("/user_account", status_code=status.HTTP_201_CREATED)
async def create_user_account(payload: Dict[str, Any] = Body(...)):
    return await generic_create(db_criminal["user_account"], payload)

@router.get("/user-account/{doc_id}")
@router.get("/user_account/{doc_id}")
async def get_user_account_by_id(doc_id: str):
    return await generic_get_one(db_criminal["user_account"], doc_id)

@router.put("/user-account/{doc_id}")
@router.put("/user_account/{doc_id}")
async def update_user_account(doc_id: str, payload: Dict[str, Any] = Body(...)):
    return await generic_update(db_criminal["user_account"], doc_id, payload)

@router.delete("/user-account/{doc_id}")
@router.delete("/user_account/{doc_id}")
async def delete_user_account(doc_id: str):
    return await generic_delete(db_criminal["user_account"], doc_id)


import time

# 9. WATCHLIST ROUTE ALIAS (Internal Redirect to Official registered_data Collection)
@router.get("/watchlist")
async def get_watchlist(request: Request, authorization: Optional[str] = Header(None), admin_id: Optional[str] = None):
    curr_admin = get_request_admin_id(request, authorization, admin_id)
    return await generic_get_all(db_criminal["registered_data"], admin_id=curr_admin)

@router.post("/watchlist", status_code=status.HTTP_201_CREATED)
async def add_to_watchlist(request: Request, payload: Dict[str, Any] = Body(...), authorization: Optional[str] = Header(None), admin_id: Optional[str] = None):
    curr_admin = get_request_admin_id(request, authorization, admin_id)
    target_id = payload.get("id") or f"W-{int(time.time())}"
    payload["id"] = str(target_id)
    return await generic_create(db_criminal["registered_data"], payload, admin_id=curr_admin)

@router.get("/watchlist/{doc_id}")
async def get_watchlist_by_id(doc_id: str):
    return await generic_get_one(db_criminal["registered_data"], doc_id)

@router.put("/watchlist/{doc_id}")
async def update_watchlist_suspect(doc_id: str, payload: Dict[str, Any] = Body(...)):
    return await generic_update(db_criminal["registered_data"], doc_id, payload)

@router.delete("/watchlist/{doc_id}")
async def delete_watchlist_suspect(doc_id: str):
    return await generic_delete(db_criminal["registered_data"], doc_id)


# ---------------------------------------------------------
# Overview & Health Endpoints
# ---------------------------------------------------------
@router.get("/")
async def get_criminal_module_status():
    """Overview status of Criminal Tracking system and collection counts"""
    try:
        collections = ["alerts", "camera_network", "criminal_detections", "locations_map", "registered_data", "reports", "system_settings", "user_account"]
        stats = {}
        for coll in collections:
            stats[coll] = await db_criminal[coll].count_documents({})
        return {
            "status": "online",
            "module": "Criminal Tracking & Watchlist System",
            "database": "Criminal_traking",
            "collection_counts": stats,
            "server_time": get_server_time()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def criminal_health_check():
    db_health = await check_database_health()
    return {
        "module": "Criminal Tracking System",
        "database": "Criminal_traking",
        "db_health": db_health
    }

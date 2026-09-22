"""
Project Chakravyuh - Missing Children Router (Auto-Saving CRUD API Engine)
Module Database: Missing_children (db_missing)
Prefix: /api/missing-children

Collections Managed:
- add_data
- alerts
- camera_network
- children_detection
- map
- registered_data
- reports
- system_setting
- user_account
- missing_children
"""

import time
import re
from fastapi import APIRouter, HTTPException, Body, status, Depends, Header
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from database import db_missing, check_database_health
from utils.crud_helper import (
    get_authenticated_admin_id,
    get_server_time,
    serialize_doc,
    serialize_docs,
    generic_get_all,
    generic_get_one,
    generic_create,
    generic_update,
    generic_delete
)
from utils.notifier import send_missing_child_alert, find_nearest_police_station

def get_missing_admin(authorization: Optional[str] = Header(None)) -> str:
    return get_authenticated_admin_id(authorization, required_module="missing-children")

router = APIRouter(tags=["Missing Children System"])

# ---------------------------------------------------------
# Dynamic Generic Collection CRUD Endpoints
# ---------------------------------------------------------
@router.get("/collection/{collection_name}")
async def get_any_collection_docs(collection_name: str, admin_id: str = Depends(get_missing_admin)):
    """Fetch all documents from specified collection in Missing Children database"""
    return await generic_get_all(db_missing[collection_name], admin_id=admin_id)

@router.post("/collection/{collection_name}", status_code=status.HTTP_201_CREATED)
async def create_any_collection_doc(collection_name: str, payload: Dict[str, Any] = Body(...), admin_id: str = Depends(get_missing_admin)):
    """Insert a document directly into specified MongoDB collection in Missing Children DB"""
    return await generic_create(db_missing[collection_name], payload, admin_id=admin_id)

@router.get("/collection/{collection_name}/{doc_id}")
async def get_any_collection_doc_by_id(collection_name: str, doc_id: str, admin_id: str = Depends(get_missing_admin)):
    """Fetch a document by ID from specified collection"""
    return await generic_get_one(db_missing[collection_name], doc_id, admin_id=admin_id)

@router.put("/collection/{collection_name}/{doc_id}")
async def update_any_collection_doc(collection_name: str, doc_id: str, payload: Dict[str, Any] = Body(...), admin_id: str = Depends(get_missing_admin)):
    """Update a document by ID in specified collection"""
    return await generic_update(db_missing[collection_name], doc_id, payload, admin_id=admin_id)

@router.delete("/collection/{collection_name}/{doc_id}")
async def delete_any_collection_doc(collection_name: str, doc_id: str, admin_id: str = Depends(get_missing_admin)):
    """Delete a document by ID from specified collection"""
    return await generic_delete(db_missing[collection_name], doc_id, admin_id=admin_id)


# ---------------------------------------------------------
# Dedicated Collection Routes for Missing Children DB
# ---------------------------------------------------------

# 1. ADD DATA COLLECTION
@router.get("/add-data")
@router.get("/add_data")
async def get_add_data(admin_id: str = Depends(get_missing_admin)):
    return await generic_get_all(db_missing["add_data"], admin_id=admin_id)

@router.post("/add-data", status_code=status.HTTP_201_CREATED)
@router.post("/add_data", status_code=status.HTTP_201_CREATED)
async def create_add_data(payload: Dict[str, Any] = Body(...), admin_id: str = Depends(get_missing_admin)):
    return await generic_create(db_missing["add_data"], payload, admin_id=admin_id)

@router.get("/add-data/{doc_id}")
@router.get("/add_data/{doc_id}")
async def get_add_data_by_id(doc_id: str, admin_id: str = Depends(get_missing_admin)):
    return await generic_get_one(db_missing["add_data"], doc_id, admin_id=admin_id)

@router.put("/add-data/{doc_id}")
@router.put("/add_data/{doc_id}")
async def update_add_data(doc_id: str, payload: Dict[str, Any] = Body(...), admin_id: str = Depends(get_missing_admin)):
    return await generic_update(db_missing["add_data"], doc_id, payload, admin_id=admin_id)

@router.delete("/add-data/{doc_id}")
@router.delete("/add_data/{doc_id}")
async def delete_add_data(doc_id: str, admin_id: str = Depends(get_missing_admin)):
    return await generic_delete(db_missing["add_data"], doc_id, admin_id=admin_id)


# 2. ALERTS COLLECTION
@router.get("/alerts")
async def get_all_alerts(admin_id: str = Depends(get_missing_admin)):
    return await generic_get_all(db_missing["alerts"], admin_id=admin_id)

@router.post("/alerts", status_code=status.HTTP_201_CREATED)
async def create_alert(payload: Dict[str, Any] = Body(...), admin_id: str = Depends(get_missing_admin)):
    return await generic_create(db_missing["alerts"], payload, admin_id=admin_id)

@router.get("/alerts/{doc_id}")
async def get_alert_by_id(doc_id: str, admin_id: str = Depends(get_missing_admin)):
    return await generic_get_one(db_missing["alerts"], doc_id, admin_id=admin_id)

@router.put("/alerts/{doc_id}")
async def update_alert(doc_id: str, payload: Dict[str, Any] = Body(...), admin_id: str = Depends(get_missing_admin)):
    return await generic_update(db_missing["alerts"], doc_id, payload, admin_id=admin_id)

@router.delete("/alerts/{doc_id}")
async def delete_alert(doc_id: str, admin_id: str = Depends(get_missing_admin)):
    return await generic_delete(db_missing["alerts"], doc_id, admin_id=admin_id)


# 3. CAMERA NETWORK COLLECTION
@router.get("/camera-network")
@router.get("/camera_network")
async def get_camera_network(admin_id: str = Depends(get_missing_admin)):
    return await generic_get_all(db_missing["camera_network"], admin_id=admin_id)

@router.post("/camera-network", status_code=status.HTTP_201_CREATED)
@router.post("/camera_network", status_code=status.HTTP_201_CREATED)
async def create_camera_node(payload: Dict[str, Any] = Body(...), admin_id: str = Depends(get_missing_admin)):
    return await generic_create(db_missing["camera_network"], payload, admin_id=admin_id)

@router.get("/camera-network/{doc_id}")
@router.get("/camera_network/{doc_id}")
async def get_camera_node_by_id(doc_id: str, admin_id: str = Depends(get_missing_admin)):
    return await generic_get_one(db_missing["camera_network"], doc_id, admin_id=admin_id)

@router.put("/camera-network/{doc_id}")
@router.put("/camera_network/{doc_id}")
async def update_camera_node(doc_id: str, payload: Dict[str, Any] = Body(...), admin_id: str = Depends(get_missing_admin)):
    return await generic_update(db_missing["camera_network"], doc_id, payload, admin_id=admin_id)

@router.delete("/camera-network/{doc_id}")
@router.delete("/camera_network/{doc_id}")
async def delete_camera_node(doc_id: str, admin_id: str = Depends(get_missing_admin)):
    return await generic_delete(db_missing["camera_network"], doc_id, admin_id=admin_id)


# 4. CHILDREN DETECTION COLLECTION
@router.get("/children-detection")
@router.get("/children_detection")
async def get_children_detections(admin_id: str = Depends(get_missing_admin)):
    return await generic_get_all(db_missing["children_detection"], admin_id=admin_id)

@router.post("/children-detection", status_code=status.HTTP_201_CREATED)
@router.post("/children_detection", status_code=status.HTTP_201_CREATED)
async def create_child_detection(payload: Dict[str, Any] = Body(...), admin_id: str = Depends(get_missing_admin)):
    return await generic_create(db_missing["children_detection"], payload, admin_id=admin_id)

@router.get("/children-detection/{doc_id}")
@router.get("/children_detection/{doc_id}")
async def get_child_detection_by_id(doc_id: str, admin_id: str = Depends(get_missing_admin)):
    return await generic_get_one(db_missing["children_detection"], doc_id, admin_id=admin_id)

@router.put("/children-detection/{doc_id}")
@router.put("/children_detection/{doc_id}")
async def update_child_detection(doc_id: str, payload: Dict[str, Any] = Body(...), admin_id: str = Depends(get_missing_admin)):
    return await generic_update(db_missing["children_detection"], doc_id, payload, admin_id=admin_id)

@router.delete("/children-detection/{doc_id}")
@router.delete("/children_detection/{doc_id}")
async def delete_child_detection(doc_id: str, admin_id: str = Depends(get_missing_admin)):
    return await generic_delete(db_missing["children_detection"], doc_id, admin_id=admin_id)


# 5. MAP COLLECTION
@router.get("/map")
async def get_map_nodes(admin_id: str = Depends(get_missing_admin)):
    return await generic_get_all(db_missing["map"], admin_id=admin_id)

@router.post("/map", status_code=status.HTTP_201_CREATED)
async def create_map_node(payload: Dict[str, Any] = Body(...), admin_id: str = Depends(get_missing_admin)):
    return await generic_create(db_missing["map"], payload, admin_id=admin_id)

@router.get("/map/{doc_id}")
async def get_map_node_by_id(doc_id: str, admin_id: str = Depends(get_missing_admin)):
    return await generic_get_one(db_missing["map"], doc_id, admin_id=admin_id)

@router.put("/map/{doc_id}")
async def update_map_node(doc_id: str, payload: Dict[str, Any] = Body(...), admin_id: str = Depends(get_missing_admin)):
    return await generic_update(db_missing["map"], doc_id, payload, admin_id=admin_id)

@router.delete("/map/{doc_id}")
async def delete_map_node(doc_id: str, admin_id: str = Depends(get_missing_admin)):
    return await generic_delete(db_missing["map"], doc_id, admin_id=admin_id)


# 6. REGISTERED DATA COLLECTION
@router.get("/registered-data")
@router.get("/registered_data")
async def get_registered_data(admin_id: str = Depends(get_missing_admin)):
    return await generic_get_all(db_missing["registered_data"], admin_id=admin_id)

@router.post("/registered-data", status_code=status.HTTP_201_CREATED)
@router.post("/registered_data", status_code=status.HTTP_201_CREATED)
async def create_registered_data(payload: Dict[str, Any] = Body(...), admin_id: str = Depends(get_missing_admin)):
    return await generic_create(db_missing["registered_data"], payload, admin_id=admin_id)

@router.get("/registered-data/{doc_id}")
@router.get("/registered_data/{doc_id}")
async def get_registered_data_by_id(doc_id: str, admin_id: str = Depends(get_missing_admin)):
    return await generic_get_one(db_missing["registered_data"], doc_id, admin_id=admin_id)

@router.put("/registered-data/{doc_id}")
@router.put("/registered_data/{doc_id}")
async def update_registered_data(doc_id: str, payload: Dict[str, Any] = Body(...), admin_id: str = Depends(get_missing_admin)):
    return await generic_update(db_missing["registered_data"], doc_id, payload, admin_id=admin_id)

@router.delete("/registered-data/{doc_id}")
@router.delete("/registered_data/{doc_id}")
async def delete_registered_data(doc_id: str, admin_id: str = Depends(get_missing_admin)):
    return await generic_delete(db_missing["registered_data"], doc_id, admin_id=admin_id)


# 7. REPORTS COLLECTION
@router.get("/reports")
async def get_reports(admin_id: str = Depends(get_missing_admin)):
    return await generic_get_all(db_missing["reports"], admin_id=admin_id)

@router.post("/reports", status_code=status.HTTP_201_CREATED)
async def create_report(payload: Dict[str, Any] = Body(...), admin_id: str = Depends(get_missing_admin)):
    return await generic_create(db_missing["reports"], payload, admin_id=admin_id)

@router.get("/reports/{doc_id}")
async def get_report_by_id(doc_id: str, admin_id: str = Depends(get_missing_admin)):
    return await generic_get_one(db_missing["reports"], doc_id, admin_id=admin_id)

@router.put("/reports/{doc_id}")
async def update_report(doc_id: str, payload: Dict[str, Any] = Body(...), admin_id: str = Depends(get_missing_admin)):
    return await generic_update(db_missing["reports"], doc_id, payload, admin_id=admin_id)

@router.delete("/reports/{doc_id}")
async def delete_report(doc_id: str, admin_id: str = Depends(get_missing_admin)):
    return await generic_delete(db_missing["reports"], doc_id, admin_id=admin_id)


# 8. SYSTEM SETTING COLLECTION
@router.get("/system-setting")
@router.get("/system_setting")
async def get_system_setting(admin_id: str = Depends(get_missing_admin)):
    return await generic_get_all(db_missing["system_setting"], admin_id=admin_id)

@router.post("/system-setting", status_code=status.HTTP_201_CREATED)
@router.post("/system_setting", status_code=status.HTTP_201_CREATED)
async def create_system_setting(payload: Dict[str, Any] = Body(...), admin_id: str = Depends(get_missing_admin)):
    return await generic_create(db_missing["system_setting"], payload, admin_id=admin_id)

@router.get("/system-setting/{doc_id}")
@router.get("/system_setting/{doc_id}")
async def get_system_setting_by_id(doc_id: str, admin_id: str = Depends(get_missing_admin)):
    return await generic_get_one(db_missing["system_setting"], doc_id, admin_id=admin_id)

@router.put("/system-setting/{doc_id}")
@router.put("/system_setting/{doc_id}")
async def update_system_setting(doc_id: str, payload: Dict[str, Any] = Body(...), admin_id: str = Depends(get_missing_admin)):
    return await generic_update(db_missing["system_setting"], doc_id, payload, admin_id=admin_id)

@router.delete("/system-setting/{doc_id}")
@router.delete("/system_setting/{doc_id}")
async def delete_system_setting(doc_id: str, admin_id: str = Depends(get_missing_admin)):
    return await generic_delete(db_missing["system_setting"], doc_id, admin_id=admin_id)


# 9. USER ACCOUNT COLLECTION
@router.get("/user-account")
@router.get("/user_account")
@router.get("/user_account.missing_children")
async def get_user_accounts(admin_id: str = Depends(get_missing_admin)):
    return await generic_get_all(db_missing["user_account.missing_children"], admin_id=admin_id)

@router.post("/user-account", status_code=status.HTTP_201_CREATED)
@router.post("/user_account", status_code=status.HTTP_201_CREATED)
@router.post("/user_account.missing_children", status_code=status.HTTP_201_CREATED)
async def create_user_account(payload: Dict[str, Any] = Body(...), admin_id: str = Depends(get_missing_admin)):
    return await generic_create(db_missing["user_account.missing_children"], payload, admin_id=admin_id)

@router.get("/user-account/{doc_id}")
@router.get("/user_account/{doc_id}")
@router.get("/user_account.missing_children/{doc_id}")
async def get_user_account_by_id(doc_id: str, admin_id: str = Depends(get_missing_admin)):
    return await generic_get_one(db_missing["user_account.missing_children"], doc_id, admin_id=admin_id)

@router.put("/user-account/{doc_id}")
@router.put("/user_account/{doc_id}")
@router.put("/user_account.missing_children/{doc_id}")
async def update_user_account(doc_id: str, payload: Dict[str, Any] = Body(...), admin_id: str = Depends(get_missing_admin)):
    return await generic_update(db_missing["user_account.missing_children"], doc_id, payload, admin_id=admin_id)

@router.delete("/user-account/{doc_id}")
@router.delete("/user_account/{doc_id}")
@router.delete("/user_account.missing_children/{doc_id}")
async def delete_user_account(doc_id: str, admin_id: str = Depends(get_missing_admin)):
    return await generic_delete(db_missing["user_account.missing_children"], doc_id, admin_id=admin_id)


# 10. MISSING CHILDREN RECORDS ROUTE ALIAS (Internal Redirect to Official registered_data Collection)
@router.get("/records")
async def get_missing_children_records(admin_id: str = Depends(get_missing_admin)):
    return await generic_get_all(db_missing["registered_data"], admin_id=admin_id)

@router.post("/records", status_code=status.HTTP_201_CREATED)
async def report_missing_child(payload: Dict[str, Any] = Body(...), admin_id: str = Depends(get_missing_admin)):
    case_id = payload.get("id") or f"MC-{int(get_server_time()['timestamp'].replace('-', '').replace(':', ''))}"
    payload["id"] = str(case_id)
    return await generic_create(db_missing["registered_data"], payload, admin_id=admin_id)

@router.get("/records/{child_id}")
async def get_missing_child_by_id(child_id: str, admin_id: str = Depends(get_missing_admin)):
    return await generic_get_one(db_missing["registered_data"], child_id, admin_id=admin_id)

@router.put("/records/{child_id}")
async def update_missing_child_record(child_id: str, payload: Dict[str, Any] = Body(...), admin_id: str = Depends(get_missing_admin)):
    return await generic_update(db_missing["registered_data"], child_id, payload, admin_id=admin_id)

@router.delete("/records/{child_id}")
async def delete_missing_child_record(child_id: str, admin_id: str = Depends(get_missing_admin)):
    return await generic_delete(db_missing["registered_data"], child_id, admin_id=admin_id)



# 11. AUTHORITY INFORMATION COLLECTION (Missing_children.authority_information)
from fastapi import BackgroundTasks
@router.get("/authority-information")
@router.get("/authority_information")
async def get_authority_information(admin_id: str = Depends(get_missing_admin)):
    return await generic_get_all(db_missing["authority_information"], admin_id=admin_id)

@router.post("/authority-information", status_code=status.HTTP_201_CREATED)
@router.post("/authority_information", status_code=status.HTTP_201_CREATED)
async def create_authority_information(
    background_tasks: BackgroundTasks,
    payload: Dict[str, Any] = Body(...),
    admin_id: str = Depends(get_missing_admin)
):
    created_doc = await generic_create(db_missing["authority_information"], payload, admin_id=admin_id)
    from utils.notifier import send_authority_welcome_email
    background_tasks.add_task(send_authority_welcome_email, payload, admin_id)
    return created_doc

@router.get("/authority-information/{doc_id}")
@router.get("/authority_information/{doc_id}")
async def get_authority_information_by_id(doc_id: str, admin_id: str = Depends(get_missing_admin)):
    return await generic_get_one(db_missing["authority_information"], doc_id, admin_id=admin_id)

@router.put("/authority-information/{doc_id}")
@router.put("/authority_information/{doc_id}")
async def update_authority_information(
    doc_id: str,
    background_tasks: BackgroundTasks,
    payload: Dict[str, Any] = Body(...),
    admin_id: str = Depends(get_missing_admin)
):
    updated_doc = await generic_update(db_missing["authority_information"], doc_id, payload, admin_id=admin_id)
    from utils.notifier import send_authority_welcome_email
    background_tasks.add_task(send_authority_welcome_email, payload, admin_id)
    return updated_doc

@router.delete("/authority-information/{doc_id}")
@router.delete("/authority_information/{doc_id}")
async def delete_authority_information(doc_id: str, admin_id: str = Depends(get_missing_admin)):
    return await generic_delete(db_missing["authority_information"], doc_id, admin_id=admin_id)

# ---------------------------------------------------------
# Missing Child Email Dispatch (Officer Alert)
# ---------------------------------------------------------

# Per-child cooldown: 60s duplicate suppression
_CHILD_DISPATCH_COOLDOWNS: Dict[str, float] = {}
_CHILD_DISPATCH_COOLDOWN_SEC = 60.0

@router.post("/dispatch-alert", status_code=status.HTTP_200_OK)
@router.post("/dispatch_alert", status_code=status.HTTP_200_OK)
async def dispatch_missing_child_alert(
    payload: Dict[str, Any] = Body(...),
    admin_id: str = Depends(get_missing_admin)
):
    """
    Dispatches an email alert to the nearest registered police station officers
    when a missing child is detected via live camera feed.

    Reuses the `send_missing_child_alert` engine but sends a Missing Child Rescue
    Alert email instead of a criminal alert. Includes 60s duplicate suppression
    per child+camera node pair.
    """
    child_id = str(payload.get("child_id") or payload.get("id") or "MC-UNKNOWN")
    child_name = str(payload.get("child_name") or payload.get("name") or "Missing Child")
    cam_id = str(payload.get("camera_id") or payload.get("cam_id") or "CAM-LIVE-WEBCAM-01")
    force = payload.get("force") or payload.get("is_test") or False

    # Duplicate suppression per child+camera
    cooldown_key = f"{child_id.lower()}:{cam_id.lower()}"
    now = time.time()
    last_ts = _CHILD_DISPATCH_COOLDOWNS.get(cooldown_key, 0.0)
    if not force and (now - last_ts) < _CHILD_DISPATCH_COOLDOWN_SEC:
        remaining = int(_CHILD_DISPATCH_COOLDOWN_SEC - (now - last_ts))
        return {
            "status": "suppressed",
            "message": f"Duplicate alert suppressed for '{child_name}' at camera '{cam_id}' within {_CHILD_DISPATCH_COOLDOWN_SEC:.0f}s cooldown.",
            "cooldown_remaining_sec": remaining
        }
    _CHILD_DISPATCH_COOLDOWNS[cooldown_key] = now

    effective_admin_id = admin_id

    # Build child data payload for the alert engine
    child_alert_payload = {
        "name": child_name,
        "id": child_id,
        "photo_url": payload.get("photo_url") or payload.get("photoUrl") or payload.get("photo") or "",
        "risk_level": "🟢 MISSING CHILD — URGENT RESCUE",
        "crime_details": (
            f"Missing child reported. Age: {payload.get('age', 'N/A')} yrs. "
            f"Last seen: {payload.get('lastSeenLocation') or payload.get('location') or 'Unknown'}. "
            f"Description: {payload.get('description') or 'N/A'}"
        ),
        "ipc_charges": "Missing Person — Immediate Rescue Required",
        "age": str(payload.get("age") or "N/A"),
        "confidence": str(payload.get("confidence") or payload.get("match_confidence") or "N/A")
    }
    location_payload = {
        "cam_id": cam_id,
        "camera_location": payload.get("camera_location") or payload.get("location") or "Live Camera Node",
        "lat": float(payload.get("lat") or payload.get("latitude") or 22.4632),
        "lng": float(payload.get("lng") or payload.get("longitude") or 76.9381)
    }

    dispatch_res = await send_missing_child_alert(child_alert_payload, location_payload, admin_id=effective_admin_id)

    return {
        "status": dispatch_res.get("status", "success"),
        "message": dispatch_res.get("message", "Missing child rescue alert dispatched"),
        "child_id": child_id,
        "child_name": child_name,
        "camera_node": cam_id,
        "dispatched_officers": dispatch_res.get("dispatched_officers") or [],
        "successful_emails": dispatch_res.get("successful_emails", 0),
        "nearest_station": dispatch_res.get("nearest_station")
    }


# ---------------------------------------------------------
# Overview & Health Endpoints
# ---------------------------------------------------------
@router.get("/")
async def get_missing_module_status(authorization: Optional[str] = Header(None)):
    """Overview status of Missing Children system and collection counts"""
    try:
        admin_id = None
        if authorization:
            try:
                admin_id = get_authenticated_admin_id(authorization)
            except Exception:
                pass
        filter_q = {"admin_id": admin_id} if admin_id else {}
        collections = ["add_data", "alerts", "camera_network", "children_detection", "map", "registered_data", "reports", "system_setting", "user_account", "missing_children", "authority_information"]
        stats = {}
        for coll in collections:
            stats[coll] = await db_missing[coll].count_documents(filter_q)
        return {
            "status": "online",
            "module": "Missing Children AI Tracking & Rescue System",
            "database": "Missing_children",
            "collection_counts": stats,
            "server_time": get_server_time()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def missing_children_health_check(admin_id: str = Depends(get_missing_admin)):
    db_health = await check_database_health()
    return {
        "module": "Missing Children System",
        "database": "Missing_children",
        "db_health": db_health
    }

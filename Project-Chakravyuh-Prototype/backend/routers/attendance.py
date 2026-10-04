"""
Project Chakravyuh - Attendance Router (Auto-Saving CRUD API Engine)
Module Database: Attendence (db_attendance)
Prefix: /api/attendance

Collections Managed:
- alerts
- attendance_scan
- camera_network
- map
- registered_data
- students_info_PA
- reports
- system_settings
- user_accounts
- personnel
"""

from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, HTTPException, Body, status
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from database import db_attendance, check_database_health
from utils.crud_helper import (
    get_server_time,
    serialize_doc,
    serialize_docs,
    generic_get_all,
    generic_get_one,
    generic_create,
    generic_update,
    generic_delete,
    find_doc_by_id
)

router = APIRouter(tags=["Attendance System"])

TWENTY_HOURS_SECONDS = 20 * 3600  # 72000 seconds

async def check_20h_cooldown(person_id: str):
    """
    Checks if a person has an accepted attendance scan within the last 20 hours.
    Returns: (is_allowed: bool, last_scan_doc: dict|None, elapsed_seconds: float, remaining_seconds: float, next_allowed_at: str)
    """
    clean_id = str(person_id).strip()
    if not clean_id:
        return True, None, 999999.0, 0.0, ""

    query = {
        "$or": [
            {"person_id": clean_id},
            {"personId": clean_id},
            {"id": clean_id}
        ],
        "accepted": {"$ne": False}
    }

    cursor = db_attendance["attendance_scan"].find(query).sort([("timestamp_num", -1), ("_id", -1)]).limit(1)
    scans = await cursor.to_list(length=1)

    now_utc = datetime.now(timezone.utc)
    now_ts = now_utc.timestamp()

    if not scans:
        return True, None, 999999.0, 0.0, ""

    latest_scan = scans[0]
    last_ts = latest_scan.get("timestamp_num")

    if not last_ts:
        ts_val = latest_scan.get("timestamp") or latest_scan.get("created_at")
        if isinstance(ts_val, (int, float)):
            last_ts = float(ts_val)
        else:
            try:
                dt = datetime.fromisoformat(str(ts_val).replace('Z', '+00:00'))
                last_ts = dt.timestamp()
            except Exception:
                last_ts = now_ts - 100000.0

    elapsed_seconds = now_ts - last_ts

    if elapsed_seconds < TWENTY_HOURS_SECONDS:
        remaining_seconds = TWENTY_HOURS_SECONDS - elapsed_seconds
        next_allowed_dt_utc = datetime.fromtimestamp(last_ts + TWENTY_HOURS_SECONDS, tz=timezone.utc)

        IST_TZ = timezone(timedelta(hours=5, minutes=30))
        next_allowed_ist = next_allowed_dt_utc.astimezone(IST_TZ)
        next_allowed_at = next_allowed_ist.strftime("%d %b %Y, %I:%M:%S %p IST")

        return False, latest_scan, elapsed_seconds, remaining_seconds, next_allowed_at

    return True, latest_scan, elapsed_seconds, 0.0, ""


# ---------------------------------------------------------
# Dynamic Generic Collection CRUD Endpoints
# ---------------------------------------------------------
@router.get("/collection/{collection_name}")
async def get_any_collection_docs(collection_name: str):
    """Fetch all documents from specified collection in Attendance database"""
    return await generic_get_all(db_attendance[collection_name])

@router.post("/collection/{collection_name}", status_code=status.HTTP_201_CREATED)
async def create_any_collection_doc(collection_name: str, payload: Dict[str, Any] = Body(...)):
    """Insert a document directly into specified MongoDB collection in Attendance DB"""
    return await generic_create(db_attendance[collection_name], payload)

@router.get("/collection/{collection_name}/{doc_id}")
async def get_any_collection_doc_by_id(collection_name: str, doc_id: str):
    """Fetch a document by ID from specified collection"""
    return await generic_get_one(db_attendance[collection_name], doc_id)

@router.put("/collection/{collection_name}/{doc_id}")
async def update_any_collection_doc(collection_name: str, doc_id: str, payload: Dict[str, Any] = Body(...)):
    """Update a document by ID in specified collection"""
    return await generic_update(db_attendance[collection_name], doc_id, payload)

@router.delete("/collection/{collection_name}/{doc_id}")
async def delete_any_collection_doc(collection_name: str, doc_id: str):
    """Delete a document by ID from specified collection"""
    return await generic_delete(db_attendance[collection_name], doc_id)


# ---------------------------------------------------------
# Dedicated Collection Routes for Attendance DB
# ---------------------------------------------------------

# 1. ALERTS COLLECTION
@router.get("/alerts")
async def get_all_alerts():
    return await generic_get_all(db_attendance["alerts"])

@router.post("/alerts", status_code=status.HTTP_201_CREATED)
async def create_alert(payload: Dict[str, Any] = Body(...)):
    return await generic_create(db_attendance["alerts"], payload)

@router.get("/alerts/{doc_id}")
async def get_alert_by_id(doc_id: str):
    return await generic_get_one(db_attendance["alerts"], doc_id)

@router.put("/alerts/{doc_id}")
async def update_alert(doc_id: str, payload: Dict[str, Any] = Body(...)):
    return await generic_update(db_attendance["alerts"], doc_id, payload)

@router.delete("/alerts/{doc_id}")
async def delete_alert(doc_id: str):
    return await generic_delete(db_attendance["alerts"], doc_id)


# 2. ATTENDANCE SCAN COLLECTION
@router.get("/attendance-scan")
@router.get("/attendance_scan")
async def get_attendance_scans():
    return await generic_get_all(db_attendance["attendance_scan"])

@router.post("/attendance-scan")
@router.post("/attendance_scan")
async def create_attendance_scan(payload: Dict[str, Any] = Body(...)):
    override_win = payload.get("override_window", False)
    is_open, window_msg, window_info = is_within_attendance_window()
    if not is_open and not override_win:
        return {
            "success": False,
            "status": "closed",
            "message": window_msg,
            "window_info": window_info
        }

    emp_id = payload.get("person_id") or payload.get("personId") or payload.get("id")
    if emp_id:
        is_allowed, last_scan, elapsed_sec, rem_sec, next_allowed_at = await check_20h_cooldown(str(emp_id))
        if not is_allowed:
            return {
                "success": False,
                "status": "cooldown",
                "message": f"Attendance already recorded. Try again after 20 hours.",
                "next_allowed_at": next_allowed_at,
                "elapsed_hours": round(elapsed_sec / 3600, 2),
                "remaining_hours": round(rem_sec / 3600, 2)
            }
    
    payload_copy = dict(payload)
    now_ts = datetime.now(timezone.utc).timestamp()
    payload_copy["timestamp_num"] = payload_copy.get("timestamp_num") or now_ts
    payload_copy["accepted"] = True
    return await generic_create(db_attendance["attendance_scan"], payload_copy)

@router.get("/attendance-scan/{doc_id}")
@router.get("/attendance_scan/{doc_id}")
async def get_attendance_scan_by_id(doc_id: str):
    return await generic_get_one(db_attendance["attendance_scan"], doc_id)

@router.put("/attendance-scan/{doc_id}")
@router.put("/attendance_scan/{doc_id}")
async def update_attendance_scan(doc_id: str, payload: Dict[str, Any] = Body(...)):
    return await generic_update(db_attendance["attendance_scan"], doc_id, payload)

@router.delete("/attendance-scan/{doc_id}")
@router.delete("/attendance_scan/{doc_id}")
async def delete_attendance_scan(doc_id: str):
    return await generic_delete(db_attendance["attendance_scan"], doc_id)


# 3. CAMERA NETWORK COLLECTION
@router.get("/camera-network")
@router.get("/camera_network")
async def get_camera_network():
    return await generic_get_all(db_attendance["camera_network"])

@router.post("/camera-network", status_code=status.HTTP_201_CREATED)
@router.post("/camera_network", status_code=status.HTTP_201_CREATED)
async def create_camera_node(payload: Dict[str, Any] = Body(...)):
    return await generic_create(db_attendance["camera_network"], payload)

@router.get("/camera-network/{doc_id}")
@router.get("/camera_network/{doc_id}")
async def get_camera_node_by_id(doc_id: str):
    return await generic_get_one(db_attendance["camera_network"], doc_id)

@router.put("/camera-network/{doc_id}")
@router.put("/camera_network/{doc_id}")
async def update_camera_node(doc_id: str, payload: Dict[str, Any] = Body(...)):
    return await generic_update(db_attendance["camera_network"], doc_id, payload)

@router.delete("/camera-network/{doc_id}")
@router.delete("/camera_network/{doc_id}")
async def delete_camera_node(doc_id: str):
    return await generic_delete(db_attendance["camera_network"], doc_id)


# 4. MAP COLLECTION
@router.get("/map")
async def get_map_nodes():
    return await generic_get_all(db_attendance["map"])

@router.post("/map", status_code=status.HTTP_201_CREATED)
async def create_map_node(payload: Dict[str, Any] = Body(...)):
    return await generic_create(db_attendance["map"], payload)

@router.get("/map/{doc_id}")
async def get_map_node_by_id(doc_id: str):
    return await generic_get_one(db_attendance["map"], doc_id)

@router.put("/map/{doc_id}")
async def update_map_node(doc_id: str, payload: Dict[str, Any] = Body(...)):
    return await generic_update(db_attendance["map"], doc_id, payload)

@router.delete("/map/{doc_id}")
async def delete_map_node(doc_id: str):
    return await generic_delete(db_attendance["map"], doc_id)


# 5. REGISTERED DATA COLLECTION
@router.get("/registered-data")
@router.get("/registered_data")
async def get_registered_data():
    return await generic_get_all(db_attendance["registered_data"])

@router.post("/registered-data", status_code=status.HTTP_201_CREATED)
@router.post("/registered_data", status_code=status.HTTP_201_CREATED)
async def create_registered_data(payload: Dict[str, Any] = Body(...)):
    return await generic_create(db_attendance["registered_data"], payload)

@router.get("/registered-data/{doc_id}")
@router.get("/registered_data/{doc_id}")
async def get_registered_data_by_id(doc_id: str):
    return await generic_get_one(db_attendance["registered_data"], doc_id)

@router.put("/registered-data/{doc_id}")
@router.put("/registered_data/{doc_id}")
async def update_registered_data(doc_id: str, payload: Dict[str, Any] = Body(...)):
    return await generic_update(db_attendance["registered_data"], doc_id, payload)

@router.delete("/registered-data/{doc_id}")
@router.delete("/registered_data/{doc_id}")
async def delete_registered_data(doc_id: str):
    return await generic_delete(db_attendance["registered_data"], doc_id)


# 6. STUDENTS INFO PA COLLECTION
@router.get("/students-info-pa")
@router.get("/students_info_PA")
async def get_students_info_pa():
    return await generic_get_all(db_attendance["students_info_PA"])

@router.post("/students-info-pa", status_code=status.HTTP_201_CREATED)
@router.post("/students_info_PA", status_code=status.HTTP_201_CREATED)
async def create_student_info(payload: Dict[str, Any] = Body(...)):
    return await generic_create(db_attendance["students_info_PA"], payload)

@router.get("/students-info-pa/{doc_id}")
@router.get("/students_info_PA/{doc_id}")
async def get_student_info_by_id(doc_id: str):
    return await generic_get_one(db_attendance["students_info_PA"], doc_id)

@router.put("/students-info-pa/{doc_id}")
@router.put("/students_info_PA/{doc_id}")
async def update_student_info(doc_id: str, payload: Dict[str, Any] = Body(...)):
    return await generic_update(db_attendance["students_info_PA"], doc_id, payload)

@router.delete("/students-info-pa/{doc_id}")
@router.delete("/students_info_PA/{doc_id}")
async def delete_student_info(doc_id: str):
    return await generic_delete(db_attendance["students_info_PA"], doc_id)


# 7. REPORTS COLLECTION
@router.get("/reports")
async def get_reports():
    return await generic_get_all(db_attendance["reports"])

@router.post("/reports", status_code=status.HTTP_201_CREATED)
async def create_report(payload: Dict[str, Any] = Body(...)):
    return await generic_create(db_attendance["reports"], payload)

@router.get("/reports/{doc_id}")
async def get_report_by_id(doc_id: str):
    return await generic_get_one(db_attendance["reports"], doc_id)

@router.put("/reports/{doc_id}")
async def update_report(doc_id: str, payload: Dict[str, Any] = Body(...)):
    return await generic_update(db_attendance["reports"], doc_id, payload)

@router.delete("/reports/{doc_id}")
async def delete_report(doc_id: str):
    return await generic_delete(db_attendance["reports"], doc_id)


# 8. SYSTEM SETTINGS COLLECTION
@router.get("/system-settings")
@router.get("/system_settings")
async def get_system_settings():
    return await generic_get_all(db_attendance["system_settings"])

@router.post("/system-settings", status_code=status.HTTP_201_CREATED)
@router.post("/system_settings", status_code=status.HTTP_201_CREATED)
async def create_system_setting(payload: Dict[str, Any] = Body(...)):
    return await generic_create(db_attendance["system_settings"], payload)

@router.get("/system-settings/{doc_id}")
@router.get("/system_settings/{doc_id}")
async def get_system_setting_by_id(doc_id: str):
    return await generic_get_one(db_attendance["system_settings"], doc_id)

@router.put("/system-settings/{doc_id}")
@router.put("/system_settings/{doc_id}")
async def update_system_setting(doc_id: str, payload: Dict[str, Any] = Body(...)):
    return await generic_update(db_attendance["system_settings"], doc_id, payload)

@router.delete("/system-settings/{doc_id}")
@router.delete("/system_settings/{doc_id}")
async def delete_system_setting(doc_id: str):
    return await generic_delete(db_attendance["system_settings"], doc_id)


# 9. USER ACCOUNTS COLLECTION
@router.get("/user-accounts")
@router.get("/user_accounts")
async def get_user_accounts():
    return await generic_get_all(db_attendance["user_accounts"])

@router.post("/user-accounts", status_code=status.HTTP_201_CREATED)
@router.post("/user_accounts", status_code=status.HTTP_201_CREATED)
async def create_user_account(payload: Dict[str, Any] = Body(...)):
    return await generic_create(db_attendance["user_accounts"], payload)

@router.get("/user-accounts/{doc_id}")
@router.get("/user_accounts/{doc_id}")
async def get_user_account_by_id(doc_id: str):
    return await generic_get_one(db_attendance["user_accounts"], doc_id)

@router.put("/user-accounts/{doc_id}")
@router.put("/user_accounts/{doc_id}")
async def update_user_account(doc_id: str, payload: Dict[str, Any] = Body(...)):
    return await generic_update(db_attendance["user_accounts"], doc_id, payload)

@router.delete("/user-accounts/{doc_id}")
@router.delete("/user_accounts/{doc_id}")
async def delete_user_account(doc_id: str):
    return await generic_delete(db_attendance["user_accounts"], doc_id)


# 10. PERSONNEL ROUTE ALIAS (Internal Redirect to Official registered_data Collection)
@router.get("/personnel")
async def get_all_personnel():
    return await generic_get_all(db_attendance["registered_data"])

@router.post("/personnel", status_code=status.HTTP_201_CREATED)
async def add_personnel(payload: Dict[str, Any] = Body(...)):
    emp_id = payload.get("id")
    if not emp_id:
        raise HTTPException(status_code=400, detail="Missing required field: 'id'")
    return await generic_create(db_attendance["registered_data"], payload)

@router.get("/personnel/{doc_id}")
async def get_personnel_by_id(doc_id: str):
    return await generic_get_one(db_attendance["registered_data"], doc_id)

@router.put("/personnel/{doc_id}")
async def update_personnel(doc_id: str, payload: Dict[str, Any] = Body(...)):
    return await generic_update(db_attendance["registered_data"], doc_id, payload)

@router.delete("/personnel/{person_id}")
async def delete_personnel(person_id: str):
    return await generic_delete(db_attendance["registered_data"], person_id)

@router.post("/personnel/delete-batch")
async def delete_batch_personnel(payload: Dict[str, Any] = Body(...)):
    ids = payload.get("ids", [])
    if not ids:
        return {"status": "success", "deleted_count": 0}
    str_ids = [str(i) for i in ids]
    res = await db_attendance["registered_data"].delete_many({"id": {"$in": str_ids}})
    return {"status": "success", "deleted_count": res.deleted_count, "ids": str_ids}

def is_within_attendance_window() -> Tuple[bool, str, Dict[str, Any]]:
    """
    Checks if current time in IST (Asia/Kolkata) is between 09:00 AM and 05:00 PM (17:00).
    """
    IST_TZ = timezone(timedelta(hours=5, minutes=30))
    now_ist = datetime.now(timezone.utc).astimezone(IST_TZ)
    current_time_val = now_ist.hour * 60 + now_ist.minute
    start_window = 9 * 60    # 9:00 AM (540 min)
    end_window = 17 * 60     # 5:00 PM (1020 min)

    is_open = start_window <= current_time_val <= end_window
    msg = "" if is_open else f"Attendance window is CLOSED. Attendance can only be marked between 9:00 AM and 5:00 PM IST (Current time: {now_ist.strftime('%I:%M:%S %p IST')})."

    return is_open, msg, {
        "is_open": is_open,
        "current_time_ist": now_ist.strftime("%I:%M:%S %p IST"),
        "window": "09:00 AM - 05:00 PM IST"
    }

class AttendanceMarkRequest(BaseModel):
    id: str = Field(..., description="Personnel / Student ID")
    name: Optional[str] = None
    role: Optional[str] = "Student"
    department: Optional[str] = "General Branch"
    status: Optional[str] = "Present"
    date: Optional[str] = None
    avatar: Optional[str] = None
    photoUrl: Optional[str] = None
    override_window: Optional[bool] = False

@router.post("/mark")
async def mark_attendance(payload: AttendanceMarkRequest):
    emp_id = str(payload.id).strip()
    status_val = payload.status or "Present"

    # Enforce 9:00 AM to 5:00 PM IST Attendance Window Rule (unless admin override requested)
    is_open, window_msg, window_info = is_within_attendance_window()
    if not is_open and not payload.override_window:
        return {
            "success": False,
            "status": "closed",
            "message": window_msg,
            "window_info": window_info
        }

    # Enforce 20-Hour Duplicate Face Scan Cooldown Rule
    is_allowed, last_scan, elapsed_sec, rem_sec, next_allowed_at = await check_20h_cooldown(emp_id)
    if not is_allowed:
        return {
            "success": False,
            "status": "cooldown",
            "message": "Attendance already recorded. Try again after 20 hours.",
            "next_allowed_at": next_allowed_at,
            "elapsed_hours": round(elapsed_sec / 3600, 2),
            "remaining_hours": round(rem_sec / 3600, 2)
        }

    now_utc = datetime.now(timezone.utc)
    now_ts = now_utc.timestamp()
    server_time = get_server_time()
    shift_date = payload.date or server_time["formatted_date"]
    
    next_allowed_dt_utc = datetime.fromtimestamp(now_ts + TWENTY_HOURS_SECONDS, tz=timezone.utc)
    IST_TZ = timezone(timedelta(hours=5, minutes=30))
    next_allowed_at = next_allowed_dt_utc.astimezone(IST_TZ).strftime("%d %b %Y, %I:%M:%S %p IST")

    person, query = await find_doc_by_id(db_attendance["registered_data"], emp_id)
    if not person:
        person = {
            "id": emp_id,
            "name": payload.name or f"Person {emp_id}",
            "role": payload.role or "Student",
            "department": payload.department or "General Department",
            "status": status_val,
            "entry": server_time["full_datetime"] if status_val in ["Present", "Late"] else "--",
            "timestamp": server_time["timestamp"],
            "attendanceHistory": {}
        }

    history = person.get("attendanceHistory", {})
    history[shift_date] = {
        "status": status_val,
        "time": server_time["formatted_time"] if status_val in ["Present", "Late"] else "--",
        "fullDateTime": server_time["full_datetime"] if status_val in ["Present", "Late"] else "--",
        "timestamp": server_time["timestamp"]
    }

    update_fields = {
        "id": emp_id,
        "name": payload.name or person.get("name", f"Person {emp_id}"),
        "role": payload.role or person.get("role", "Student"),
        "department": payload.department or person.get("department", "General Department"),
        "status": status_val,
        "entry": server_time["full_datetime"] if status_val in ["Present", "Late"] else "--",
        "timestamp": server_time["timestamp"],
        "attendanceHistory": history
    }

    await db_attendance["registered_data"].update_one(
        {"id": emp_id},
        {"$set": update_fields},
        upsert=True
    )

    # Automatically record scan event into official attendance_scan collection
    scan_doc = {
        "id": f"SCAN-{emp_id}-{int(now_ts)}",
        "person_id": emp_id,
        "personId": emp_id,
        "name": update_fields["name"],
        "role": update_fields["role"],
        "department": update_fields["department"],
        "status": status_val,
        "date": shift_date,
        "timestamp_num": now_ts,
        "timestamp": server_time["timestamp"],
        "created_at": server_time["full_datetime"],
        "accepted": True
    }
    await db_attendance["attendance_scan"].insert_one(scan_doc)

    # Automatically save/update Present/Absent info into official students_info_PA collection
    pa_doc = {
        "id": emp_id,
        "person_id": emp_id,
        "personId": emp_id,
        "name": update_fields["name"],
        "role": update_fields["role"],
        "department": update_fields["department"],
        "status": status_val,
        "date": shift_date,
        "time": server_time["formatted_time"] if status_val in ["Present", "Late"] else "--",
        "fullDateTime": server_time["full_datetime"] if status_val in ["Present", "Late"] else "--",
        "timestamp_num": now_ts,
        "timestamp": server_time["timestamp"],
        "created_at": server_time["full_datetime"]
    }
    await db_attendance["students_info_PA"].update_one(
        {"id": emp_id, "date": shift_date},
        {"$set": pa_doc},
        upsert=True
    )

    return {
        "success": True,
        "status": "accepted",
        "message": f"Attendance recorded as {status_val} for {update_fields['name']}",
        "next_allowed_at": next_allowed_at,
        "server_time": server_time
    }


# ---------------------------------------------------------
# Overview & Health Endpoints
# ---------------------------------------------------------
@router.get("/")
async def get_attendance_module_status():
    """Overview status of Attendance system and collection counts"""
    try:
        collections = ["alerts", "attendance_scan", "camera_network", "map", "registered_data", "students_info_PA", "reports", "system_settings", "user_accounts"]
        stats = {}
        for coll in collections:
            stats[coll] = await db_attendance[coll].count_documents({})
        return {
            "status": "online",
            "module": "Attendance & Personnel System",
            "database": "Attendence",
            "collection_counts": stats,
            "server_time": get_server_time()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def attendance_health_check():
    db_health = await check_database_health()
    return {
        "module": "Attendance System",
        "database": "Attendence",
        "db_health": db_health
    }

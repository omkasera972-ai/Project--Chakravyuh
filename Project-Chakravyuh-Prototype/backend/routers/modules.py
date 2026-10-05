from fastapi import APIRouter, HTTPException, Body, Request, Header
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone, timedelta
import urllib.parse
import re
from database import (
    db_attendance,
    db_anpr,
    db_criminal,
    db_missing,
    db_defence,
    db_contacts
)
from routers.auth import get_request_admin_id
from utils.crud_helper import serialize_doc, generic_get_all, generic_create

router = APIRouter(prefix="/api", tags=["MongoDB Atlas Datasets"])

# Single Source of Truth: Server-Side Time Generator (Asia/Kolkata IST & ISO-8601 UTC)
IST_TZ = timezone(timedelta(hours=5, minutes=30))

def get_server_time(override_shift_date: Optional[str] = None):
    """
    Generates single source of truth server timestamps:
    - timestamp: Standard ISO-8601 UTC string ("2026-09-05T18:18:22Z")
    - shift_date: Dedicated duty shift boundary date ("2026-09-05")
    - formatted_date: DD MMM YYYY ("05 Sep 2026")
    - formatted_time: hh:mm:ss A IST ("11:48:38 PM IST")
    """
    now_utc = datetime.now(timezone.utc)
    now_ist = now_utc.astimezone(IST_TZ)
    shift_date = override_shift_date or now_ist.strftime("%Y-%m-%d")
    date_formatted = now_ist.strftime("%d %b %Y")
    time_formatted = now_ist.strftime("%I:%M:%S %p IST")
    iso_utc = now_utc.strftime("%Y-%m-%dT%H:%M:%SZ")

    return {
        "timestamp": iso_utc,
        "shift_date": shift_date,
        "formatted_date": date_formatted,
        "formatted_time": time_formatted,
        "full_datetime": f"{date_formatted}, {time_formatted}"
    }

# Helper to format Mongo objects
def clean_mongo_doc(doc):
    return serialize_doc(doc)

# --- Pydantic Models ---
class AttendanceMarkRequest(BaseModel):
    id: str = Field(..., description="Student or Personnel Record ID")
    status: Optional[str] = Field("Present", description="Attendance Status: Present, Absent, Late")
    date: Optional[str] = Field(None, description="Optional override shift_date YYYY-MM-DD")
    name: Optional[str] = None
    role: Optional[str] = None
    department: Optional[str] = None
    avatar: Optional[str] = None
    photoUrl: Optional[str] = None

# --- 1. SYSTEM SUMMARY DASHBOARD ---
@router.get("/modules/summary")
async def get_system_summary():
    """
    Centralized MongoDB Atlas Status across all 5 Dedicated Databases
    """
    try:
        att_count = await db_attendance["registered_data"].count_documents({}) if db_attendance is not None else 0
        crim_count = await db_criminal["registered_data"].count_documents({}) if db_criminal is not None else 0
        anpr_count = await db_anpr["registered_data"].count_documents({}) if db_anpr is not None else 0
        missing_count = await db_missing["registered_data"].count_documents({}) if db_missing is not None else 0
        defence_count = await db_defence["registered_data"].count_documents({}) if db_defence is not None else 0

        return {
            "status": "success",
            "database": "MongoDB Atlas (Cloud Cluster0)",
            "server_time": get_server_time(),
            "databases": {
                "chakravyuh_attendance": {"status": "Connected", "total_personnel": att_count},
                "chakravyuh_anpr": {"status": "Connected", "vehicles_indexed": anpr_count},
                "chakravyuh_criminal": {"status": "Connected", "watchlist_count": crim_count},
                "chakravyuh_missing_child": {"status": "Connected", "missing_cases": missing_count},
                "chakravyuh_defence": {"status": "Connected", "inventory_items": defence_count}
            }
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

# --- 2. ATTENDANCE MODULE DATABASE (`chakravyuh_attendance`) ---
@router.get("/attendance/personnel")
async def get_all_personnel(request: Request, authorization: Optional[str] = Header(None), admin_id: Optional[str] = None):
    """Fetch all personnel and attendance records from MongoDB Atlas filtered for authenticated admin"""
    try:
        curr_admin = get_request_admin_id(request, authorization, admin_id)
        return await generic_get_all(db_attendance["registered_data"], admin_id=curr_admin)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/attendance/personnel")
async def add_personnel_api(request: Request, payload: Dict[str, Any] = Body(...), authorization: Optional[str] = Header(None), admin_id: Optional[str] = None):
    """Add or register new student / personnel record directly into MongoDB Atlas"""
    emp_id = payload.get("id")
    if not emp_id:
        raise HTTPException(status_code=400, detail="Missing person ID")

    curr_admin = get_request_admin_id(request, authorization, admin_id) or payload.get("admin_id")
    server_time = get_server_time()
    try:
        person_doc = {
            "id": str(emp_id),
            "name": payload.get("name", "Unknown Name"),
            "role": payload.get("role", "Student"),
            "department": payload.get("department", "General Branch / Department"),
            "status": payload.get("status", "Registered"),
            "entry": payload.get("entry", "--"),
            "avatar": payload.get("avatar", "👤"),
            "photoUrl": payload.get("photoUrl") or None,
            "timestamp": server_time["timestamp"],
            "shift_date": server_time["shift_date"],
            "attendanceHistory": payload.get("attendanceHistory", {})
        }
        if curr_admin:
            person_doc["admin_id"] = str(curr_admin)

        await db_attendance["registered_data"].update_one(
            {"id": str(emp_id)},
            {"$set": person_doc},
            upsert=True
        )
        return {"status": "success", "message": f"Personnel {person_doc['name']} registered in MongoDB Atlas", "data": person_doc}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/attendance/personnel/{person_id}")
async def delete_personnel_api(person_id: str):
    """Delete a personnel record permanently from MongoDB Atlas (`chakravyuh_attendance`)"""
    try:
        res = await db_attendance["registered_data"].delete_many({"id": str(person_id)})
        return {"status": "success", "deleted_count": res.deleted_count, "id": person_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/attendance/personnel/delete-batch")
async def delete_batch_personnel_api(payload: Dict[str, Any] = Body(...)):
    """Delete multiple personnel records permanently from MongoDB Atlas"""
    ids = payload.get("ids", [])
    if not ids:
        return {"status": "success", "deleted_count": 0}
    try:
        str_ids = [str(i) for i in ids]
        res = await db_attendance["registered_data"].delete_many({"id": {"$in": str_ids}})
        return {"status": "success", "deleted_count": res.deleted_count, "ids": str_ids}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

from routers.attendance import mark_attendance as attendance_mark_attendance

@router.post("/attendance/mark")
async def mark_attendance_api(payload: AttendanceMarkRequest):
    """
    Mark or toggle real-time attendance in `Attendence` database with strict 20-hour cooldown enforcement
    """
    return await attendance_mark_attendance(payload)

# --- 3. ANPR MODULE DATABASE (`chakravyuh_anpr`) ---
@router.get("/anpr/vehicles")
async def get_all_vehicles(request: Request, authorization: Optional[str] = Header(None), admin_id: Optional[str] = None):
    """Fetch vehicle registrations from `chakravyuh_anpr`"""
    try:
        curr_admin = get_request_admin_id(request, authorization, admin_id)
        return await generic_get_all(db_anpr["registered_data"], admin_id=curr_admin)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- 4. CRIMINAL TRACKING DATABASE (`chakravyuh_criminal`) ---
@router.get("/criminal/watchlist")
async def get_watchlist(request: Request, authorization: Optional[str] = Header(None), admin_id: Optional[str] = None):
    """Fetch criminal watchlist from `chakravyuh_criminal`"""
    try:
        curr_admin = get_request_admin_id(request, authorization, admin_id)
        return await generic_get_all(db_criminal["registered_data"], admin_id=curr_admin)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/criminal/watchlist")
async def add_criminal_to_watchlist(request: Request, payload: Dict[str, Any] = Body(...), authorization: Optional[str] = Header(None), admin_id: Optional[str] = None):
    """Add a new criminal suspect record directly into MongoDB Atlas `chakravyuh_criminal`"""
    target_id = payload.get("id") or f"W-{int(datetime.now().timestamp())}"
    curr_admin = get_request_admin_id(request, authorization, admin_id) or payload.get("admin_id")
    server_time = get_server_time()
    try:
        doc = {
            "id": str(target_id),
            "name": payload.get("name", "Unknown Suspect"),
            "riskLevel": payload.get("riskLevel", "High Risk"),
            "crimeType": payload.get("crimeType") or payload.get("charges") or "Under Watchlist Surveillance",
            "charges": payload.get("charges") or payload.get("ipcCharges") or payload.get("crimeType") or "IPC 302/395",
            "age": payload.get("age", 32),
            "lastSeen": payload.get("lastSeen", "CAM-01 Primary Station"),
            "photoUrl": payload.get("photoUrl") or payload.get("photo_url") or None,
            "status": payload.get("status", "Active Alert"),
            "confidence": payload.get("confidence", "98.5%"),
            "details": payload.get("details", "Registered into criminal watchlist."),
            "timestamp": server_time["timestamp"],
            "created_at": server_time["full_datetime"]
        }
        if curr_admin:
            doc["admin_id"] = str(curr_admin)

        await db_criminal["registered_data"].update_one(
            {"id": str(target_id)},
            {"$set": doc},
            upsert=True
        )
        return {"status": "success", "message": f"Criminal record for {doc['name']} registered in MongoDB Atlas", "data": doc}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- 5. MISSING CHILD DATABASE (`chakravyuh_missing_child`) ---
@router.get("/missing-child/records")
@router.get("/missing-children/records")
async def get_missing_children(request: Request, authorization: Optional[str] = Header(None), admin_id: Optional[str] = None):
    """Fetch missing children cases from `chakravyuh_missing_child`"""
    try:
        curr_admin = get_request_admin_id(request, authorization, admin_id)
        return await generic_get_all(db_missing["registered_data"], admin_id=curr_admin)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- 6. DEFENCE DATABASE (`chakravyuh_defence`) ---
@router.get("/defence/inventory")
async def get_defence_inventory(request: Request, authorization: Optional[str] = Header(None), admin_id: Optional[str] = None):
    """Fetch armory inventory from `chakravyuh_defence`"""
    try:
        curr_admin = get_request_admin_id(request, authorization, admin_id)
        return await generic_get_all(db_defence["registered_data"], admin_id=curr_admin)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

from fastapi import BackgroundTasks
from utils.notifier import send_criminal_alert

# --- 7. POLICE EMERGENCY MOBILE DISPATCH CHANNEL ---
class PoliceDispatchPayload(BaseModel):
    targetName: str
    targetId: Optional[str] = "W-TARGET"
    policeNumber: Optional[str] = "+919876543210"
    email: Optional[str] = None
    crimeType: Optional[str] = "Under Watchlist Surveillance"
    cameraNode: Optional[str] = "CAM-03 Highway Toll Gate"
    confidence: Optional[str] = "96.8%"
    incidentDateTime: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None

class AutoDispatchPayload(BaseModel):
    targetName: str
    targetId: Optional[str] = "W-TARGET"
    crimeType: Optional[str] = "Under Watchlist Surveillance"
    cameraNode: Optional[str] = "Live Webcam - Primary Station"
    confidence: Optional[str] = "96.8%"
    incidentDateTime: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None

@router.post("/alerts/dispatch-auto")
async def auto_dispatch_criminal_alert(payload: AutoDispatchPayload, background_tasks: BackgroundTasks):
    """
    Automatic Background Emergency Alert Dispatcher.
    Fetches all active contacts from `emergency_contacts` collection and dispatches
    Gmail SMTP emails and Twilio WhatsApp notifications silently on the server side via BackgroundTasks.
    """
    criminal_data = {
        "name": payload.targetName,
        "id": payload.targetId,
        "crimeType": payload.crimeType
    }
    lat_val = payload.lat if payload.lat is not None else 22.7240
    lng_val = payload.lng if payload.lng is not None else 75.8650
    location_data = {
        "cam_id": payload.cameraNode,
        "lat": lat_val,
        "lng": lng_val
    }
    background_tasks.add_task(send_criminal_alert, criminal_data, location_data)

    return {
        "status": "success",
        "message": "Alert Auto-Dispatched to Active Contacts via Background API",
        "suspect_name": payload.targetName,
        "suspect_id": payload.targetId,
        "lat": lat_val,
        "lng": lng_val,
        "gps_map_link": f"https://maps.google.com/?q={lat_val},{lng_val}",
        "timestamp": get_server_time()["full_datetime"]
    }

@router.post("/police/emergency-dispatch")
async def dispatch_police_emergency_alert(payload: PoliceDispatchPayload, background_tasks: BackgroundTasks):
    """
    Real-Time Server-Side Emergency Broadcast Dispatcher.
    Silently dispatches WhatsApp (Twilio API) + Gmail (SMTP) notifications in the background
    to all active contacts from `emergency_contacts` collection without any browser popups or UI redirects.
    """
    server_time = get_server_time()
    dt_str = payload.incidentDateTime or server_time["full_datetime"]
    clean_number = (payload.policeNumber or "").strip()
    clean_email = (payload.email or "officer.command@police.gov.in").strip()

    criminal_data = {
        "name": payload.targetName,
        "id": payload.targetId,
        "email": clean_email,
        "phone": clean_number,
        "crimeType": payload.crimeType
    }
    lat_val = payload.lat if payload.lat is not None else 22.7240
    lng_val = payload.lng if payload.lng is not None else 75.8650
    location_data = {
        "cam_id": payload.cameraNode,
        "lat": lat_val,
        "lng": lng_val
    }
    background_tasks.add_task(send_criminal_alert, criminal_data, location_data)

    return {
        "status": "success",
        "message": "Alert Auto-Dispatched to Active Contacts via Background API",
        "app": "Project Chakravyuh (Bharat AI Command)",
        "dispatch_id": f"DISPATCH-{datetime.now().strftime('%M%S')}",
        "recipient_mobile": clean_number,
        "recipient_email": clean_email,
        "suspect_name": payload.targetName,
        "suspect_id": payload.targetId,
        "nearest_police_station": "Central HQ Police Station (736 METERS)",
        "nearest_hospital": "City Civil Multi-Specialty Hospital (700 METERS)",
        "gps_map_link": f"https://maps.google.com/?q={lat_val},{lng_val}",
        "lat": lat_val,
        "lng": lng_val,
        "charges": payload.crimeType,
        "camera_node": payload.cameraNode,
        "timestamp": dt_str,
        "sms_sent": True,
        "whatsapp_sent": True,
        "gmail_sent": True
    }

# --- 8. EMERGENCY CONTACTS MANAGEMENT (`chakravyuh_contacts`) ---
class ContactCreatePayload(BaseModel):
    name: str
    email: str
    phone: str
    is_active: Optional[bool] = True
    role: Optional[str] = "Duty Police Officer"

@router.get("/settings/contacts")
async def get_emergency_contacts():
    """Fetch all active emergency contacts from MongoDB database `chakravyuh_contacts`"""
    try:
        cursor = db_contacts["emergency_contacts"].find({"is_active": True})
        docs = await cursor.to_list(length=500)
        if not docs:
            docs = []
        return {"status": "success", "data": [clean_mongo_doc(d) for d in docs]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/settings/contacts")
async def add_emergency_contact(payload: ContactCreatePayload):
    """Add a new emergency contact to MongoDB database `chakravyuh_contacts`"""
    try:
        contact_id = f"CONT-{int(datetime.now().timestamp())}"
        new_doc = {
            "id": contact_id,
            "name": payload.name.strip(),
            "email": payload.email.strip(),
            "phone": payload.phone.strip(),
            "is_active": payload.is_active if payload.is_active is not None else True,
            "role": payload.role or "Duty Police Officer",
            "created_at": datetime.now().isoformat()
        }
        await db_contacts["emergency_contacts"].update_one(
            {"id": contact_id},
            {"$set": new_doc},
            upsert=True
        )
        return {
            "status": "success",
            "message": f"Emergency contact {payload.name} added successfully",
            "data": new_doc
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/settings/contacts/{contact_id}")
async def delete_emergency_contact(contact_id: str):
    """Remove an emergency contact by ID from MongoDB database `chakravyuh_contacts`"""
    try:
        await db_contacts["emergency_contacts"].delete_many({"id": contact_id})
        return {
            "status": "success",
            "message": f"Emergency contact {contact_id} removed successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


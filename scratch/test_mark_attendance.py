import asyncio
import os
import sys

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
backend_dir = os.path.join(root_dir, 'backend')
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from dotenv import load_dotenv
load_dotenv(os.path.join(backend_dir, '.env'))

from backend.routers.auth import create_admin_token
from backend.routers.attendance import mark_attendance, AttendanceMarkRequest

async def main():
    admin_id = "ADM-CRIM-1789132093"
    print("Testing mark_attendance endpoint...")
    payload = AttendanceMarkRequest(
        id="STU-TEST-001",
        name="Test Student Face Scan",
        role="Student",
        department="Computer Science",
        status="Present",
        date="2026-09-15"
    )
    res = await mark_attendance(payload, admin_id=admin_id)
    print("MARK RESULT:", res)

if __name__ == "__main__":
    asyncio.run(main())

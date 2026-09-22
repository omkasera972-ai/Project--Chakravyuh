import re

with open('backend/routers/missing_children.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Add /authority-information
auth_routes = '''
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
'''

content = content.replace('# ---------------------------------------------------------\n# Missing Child Email Dispatch (Officer Alert)', auth_routes + '\n# ---------------------------------------------------------\n# Missing Child Email Dispatch (Officer Alert)')

# Remove ADM-MISS to ADM-CRIM mapping hack
m = re.search(r'# -------------------------------------------------------\n    # CROSS-MODULE ADMIN_ID RESOLUTION.*?# Build child data payload', content, re.DOTALL)
if m:
    content = content.replace(m.group(0), 'effective_admin_id = admin_id\n\n    # Build child data payload')

# Update collections lists
content = content.replace('"reports", "system_setting", "user_account", "missing_children"]', '"reports", "system_setting", "user_account", "missing_children", "authority_information"]')

with open('backend/routers/missing_children.py', 'w', encoding='utf-8') as f:
    f.write(content)

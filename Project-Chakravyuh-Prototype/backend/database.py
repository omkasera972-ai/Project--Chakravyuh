"""
Project Chakravyuh - Senior Backend Database Layer
FastAPI + PyMongo / Motor MongoDB Atlas Integration
"""

import os
import time
import json
import asyncio
import logging
from typing import Dict, Any, List, Optional, Tuple

import certifi
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
import pymongo
from pymongo.errors import (
    PyMongoError,
    ConnectionFailure,
    ServerSelectionTimeoutError,
    ConfigurationError,
    OperationFailure
)

# Load environment variables (.env in backend directory or current working directory)
env_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path=env_path)
load_dotenv()

# Configure Logger
logger = logging.getLogger("chakravyuh_database")
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Fetch MongoDB Connection String from environment variables
MONGO_URI = os.getenv("MONGO_URI") or os.getenv("MONGODB_URL")

if not MONGO_URI:
    raise ValueError(
        "CRITICAL ERROR: 'MONGO_URI' environment variable is missing. "
        "Please define MONGO_URI in your .env file."
    )

LOCAL_DATA_DIR = os.path.join(os.path.dirname(__file__), "local_data")

# Fallback classes for local storage when cluster is offline
class LocalCursor:
    def __init__(self, data: List[Dict[str, Any]]):
        self._data = data

    def sort(self, key_or_list, direction=None):
        return self

    def limit(self, limit: int):
        if limit is not None:
            self._data = self._data[:limit]
        return self

    async def to_list(self, length: Optional[int] = None) -> List[Dict[str, Any]]:
        if length is not None:
            return self._data[:length]
        return self._data

class LocalInsertResult:
    def __init__(self, inserted_id: Any):
        self.inserted_id = inserted_id

class LocalDeleteResult:
    def __init__(self, deleted_count: int):
        self.deleted_count = deleted_count

class LocalCollection:
    def __init__(self, db_name: str, coll_name: str):
        self.db_name = db_name
        self.coll_name = coll_name
        self.dir_path = os.path.join(LOCAL_DATA_DIR, db_name)
        os.makedirs(self.dir_path, exist_ok=True)
        self.file_path = os.path.join(self.dir_path, f"{coll_name}.json")
        self.docs = []
        self._load()

    def _load(self) -> List[Dict[str, Any]]:
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, "r", encoding="utf-8") as f:
                    self.docs = json.load(f)
            except Exception:
                self.docs = []
        else:
            self.docs = []
        return self.docs

    def _save(self):
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(self.docs, f, indent=2, ensure_ascii=False)

    def _matches(self, doc: Dict[str, Any], query: Dict[str, Any]) -> bool:
        if not query:
            return True
        for k, v in query.items():
            if isinstance(v, dict):
                if "$in" in v and doc.get(k) not in v["$in"]:
                    return False
            elif doc.get(k) != v:
                return False
        return True

    async def count_documents(self, filter_query: Dict[str, Any]) -> int:
        self._load()
        return len([d for d in self.docs if self._matches(d, filter_query or {})])

    def find(self, filter_query: Dict[str, Any] = None) -> LocalCursor:
        self._load()
        query = filter_query or {}
        matched = [dict(d) for d in self.docs if self._matches(d, query)]
        return LocalCursor(matched)

    async def find_one(self, filter_query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        self._load()
        for d in self.docs:
            if self._matches(d, filter_query or {}):
                return dict(d)
        return None

    async def insert_one(self, document: Dict[str, Any]) -> LocalInsertResult:
        self._load()
        c = dict(document)
        inserted_id = c.get("id") or c.get("_id") or f"loc_{int(time.time()*1000)}"
        c["_id"] = str(inserted_id)
        if c.get("id"):
            self.docs = [d for d in self.docs if d.get("id") != c.get("id")]
        self.docs.append(c)
        self._save()
        return LocalInsertResult(inserted_id)

    async def insert_many(self, documents: List[Dict[str, Any]]):
        self._load()
        for doc in documents:
            c = dict(doc)
            inserted_id = c.get("id") or c.get("_id") or f"loc_{int(time.time()*1000)}"
            c["_id"] = str(inserted_id)
            if c.get("id"):
                self.docs = [d for d in self.docs if d.get("id") != c.get("id")]
            self.docs.append(c)
        self._save()

    async def update_one(self, filter_query: Dict[str, Any], update_cmd: Dict[str, Any], upsert: bool = False):
        self._load()
        set_fields = update_cmd.get("$set", {})
        target = None
        for d in self.docs:
            if self._matches(d, filter_query):
                target = d
                break
        if target:
            target.update(set_fields)
        elif upsert:
            new_doc = dict(filter_query)
            new_doc.update(set_fields)
            if not new_doc.get("_id"):
                new_doc["_id"] = str(new_doc.get("id") or f"loc_{int(time.time()*1000)}")
            self.docs.append(new_doc)
        self._save()

    async def delete_one(self, filter_query: Dict[str, Any]) -> LocalDeleteResult:
        self._load()
        for i, d in enumerate(self.docs):
            if self._matches(d, filter_query):
                self.docs.pop(i)
                self._save()
                return LocalDeleteResult(1)
        return LocalDeleteResult(0)

    async def delete_many(self, filter_query: Dict[str, Any]) -> LocalDeleteResult:
        self._load()
        initial_len = len(self.docs)
        self.docs = [d for d in self.docs if not self._matches(d, filter_query)]
        deleted_count = initial_len - len(self.docs)
        self._save()
        return LocalDeleteResult(deleted_count)

class SmartProxyCursor:
    def __init__(self, local_coll: LocalCollection, db_name: str, coll_name: str, filter_query: Dict[str, Any] = None):
        self.local_coll = local_coll
        self.db_name = db_name
        self.coll_name = coll_name
        self.filter_query = filter_query or {}
        self._sort_args = None
        self._limit_val = None

    def sort(self, key_or_list, direction=None):
        self._sort_args = (key_or_list, direction)
        return self

    def limit(self, limit: int):
        self._limit_val = limit
        return self

    async def to_list(self, length: Optional[int] = None) -> List[Dict[str, Any]]:
        global use_local, client
        if not use_local and client is not None:
            try:
                motor_cursor = client[self.db_name][self.coll_name].find(self.filter_query)
                if self._sort_args:
                    if isinstance(self._sort_args[0], list):
                        motor_cursor = motor_cursor.sort(self._sort_args[0])
                    else:
                        motor_cursor = motor_cursor.sort(self._sort_args[0], self._sort_args[1])
                if self._limit_val is not None:
                    motor_cursor = motor_cursor.limit(self._limit_val)
                eff_len = length if length is not None else (self._limit_val if self._limit_val is not None else 500)
                return await motor_cursor.to_list(length=eff_len)
            except Exception as pe:
                logger.warning(f"MongoDB Motor cursor error: {pe}. Switching to local storage proxy.")
                use_local = True

        local_cursor = self.local_coll.find(self.filter_query)
        if self._sort_args:
            local_cursor.sort(self._sort_args[0], self._sort_args[1])
        if self._limit_val is not None:
            local_cursor.limit(self._limit_val)
        eff_len = length if length is not None else (self._limit_val if self._limit_val is not None else 500)
        return await local_cursor.to_list(length=eff_len)

class SmartProxyCollection:
    def __init__(self, db_name: str, coll_name: str):
        self.db_name = db_name
        self.coll_name = coll_name
        self.local_coll = LocalCollection(db_name, coll_name)

    def _get_coll(self):
        global use_local, client
        if use_local or client is None:
            return self.local_coll
        return client[self.db_name][self.coll_name]

    async def count_documents(self, filter_query: Dict[str, Any]) -> int:
        global use_local
        try:
            return await self._get_coll().count_documents(filter_query)
        except Exception as pe:
            logger.warning(f"MongoDB count_documents error: {pe}. Switching to local proxy.")
            use_local = True
            return await self.local_coll.count_documents(filter_query)

    def find(self, filter_query: Dict[str, Any] = None):
        return SmartProxyCursor(self.local_coll, self.db_name, self.coll_name, filter_query)

    async def find_one(self, filter_query: Dict[str, Any]):
        global use_local
        try:
            return await self._get_coll().find_one(filter_query)
        except Exception as pe:
            logger.warning(f"MongoDB find_one error: {pe}. Switching to local proxy.")
            use_local = True
            return await self.local_coll.find_one(filter_query)

    async def insert_one(self, document: Dict[str, Any]):
        global use_local
        try:
            return await self._get_coll().insert_one(document)
        except Exception as pe:
            logger.warning(f"MongoDB insert_one error: {pe}. Switching to local proxy.")
            use_local = True
            return await self.local_coll.insert_one(document)

    async def insert_many(self, documents: List[Dict[str, Any]]):
        global use_local
        try:
            return await self._get_coll().insert_many(documents)
        except Exception as pe:
            logger.warning(f"MongoDB insert_many error: {pe}. Switching to local proxy.")
            use_local = True
            return await self.local_coll.insert_many(documents)

    async def update_one(self, filter_query: Dict[str, Any], update_cmd: Dict[str, Any], upsert: bool = False):
        global use_local
        try:
            return await self._get_coll().update_one(filter_query, update_cmd, upsert=upsert)
        except Exception as pe:
            logger.warning(f"MongoDB update_one error: {pe}. Switching to local proxy.")
            use_local = True
            return await self.local_coll.update_one(filter_query, update_cmd, upsert=upsert)

    async def delete_one(self, filter_query: Dict[str, Any]):
        global use_local
        try:
            return await self._get_coll().delete_one(filter_query)
        except Exception as pe:
            logger.warning(f"MongoDB delete_one error: {pe}. Switching to local proxy.")
            use_local = True
            return await self.local_coll.delete_one(filter_query)

    async def delete_many(self, filter_query: Dict[str, Any]):
        global use_local
        try:
            return await self._get_coll().delete_many(filter_query)
        except Exception as pe:
            logger.warning(f"MongoDB delete_many error: {pe}. Switching to local proxy.")
            use_local = True
            return await self.local_coll.delete_many(filter_query)

class SmartProxyDatabase:
    def __init__(self, db_name: str):
        self.db_name = db_name
        self._colls: Dict[str, SmartProxyCollection] = {}

    def __getitem__(self, coll_name: str) -> SmartProxyCollection:
        if coll_name not in self._colls:
            self._colls[coll_name] = SmartProxyCollection(self.db_name, coll_name)
        return self._colls[coll_name]

# Initialize Motor Async Client for MongoDB Atlas
use_local: bool = False
client: Optional[AsyncIOMotorClient] = None

try:
    logger.info("Connecting to MongoDB Atlas Cluster with Motor Async Client...")
    client = AsyncIOMotorClient(
        MONGO_URI,
        serverSelectionTimeoutMS=5000,
        connectTimeoutMS=5000,
        socketTimeoutMS=5000,
        tls=True,
        tlsAllowInvalidCertificates=True,
        tlsCAFile=certifi.where() if certifi else None,
        retryWrites=True,
        w="majority"
    )
except ConfigurationError as ce:
    logger.error(f"MongoDB Configuration Error: {ce}")
    use_local = True
except PyMongoError as pe:
    logger.error(f"PyMongo Client Error: {pe}")
    use_local = True
except Exception as e:
    logger.error(f"Unexpected Client Error: {e}")
    use_local = True

# ---------------------------------------------------------
# Export 5 Distinct Databases (wrapped with SmartProxy for auto fallback)
# ---------------------------------------------------------
db_attendance = SmartProxyDatabase('Attendence')
db_criminal = SmartProxyDatabase('Criminal_traking')
db_anpr = SmartProxyDatabase('ANPR_vehicle_system')
db_missing = SmartProxyDatabase('Missing_children')
db_defence = SmartProxyDatabase('Defence_tactical_system')

# Auxiliary database exports for application system compatibility
db_contacts = SmartProxyDatabase('chakravyuh_contacts')
db_users = SmartProxyDatabase('chakravyuh_users')


def get_sync_client() -> pymongo.MongoClient:
    """
    Returns a synchronous PyMongo MongoClient instance.
    Useful for synchronous background scripts or seeding tasks.
    """
    return pymongo.MongoClient(
        MONGO_URI,
        serverSelectionTimeoutMS=5000,
        tls=True,
        tlsAllowInvalidCertificates=True,
        tlsCAFile=certifi.where() if certifi else None
    )


# ---------------------------------------------------------
# Connection Health-Check Functions & Exception Handling
# ---------------------------------------------------------
async def check_database_health() -> Dict[str, Any]:
    """
    Asynchronously checks the connection status, cluster ping, and latency
    for MongoDB Atlas and all 5 distinct databases.
    """
    if client is None:
        return {
            "status": "unhealthy",
            "message": "MongoDB client is uninitialized",
            "latency_ms": None,
            "databases": {}
        }

    start_time = time.time()
    try:
        # Send ping to cluster admin database
        ping_res = await client.admin.command('ping')
        latency_ms = round((time.time() - start_time) * 1000, 2)

        return {
            "status": "healthy",
            "message": "Successfully connected and pinged MongoDB Atlas Cluster",
            "ping": ping_res,
            "latency_ms": latency_ms,
            "databases": {
                "db_attendance": "Attendence",
                "db_criminal": "Criminal_traking",
                "db_anpr": "ANPR_vehicle_system",
                "db_missing": "Missing_children",
                "db_defence": "Defence_tactical_system"
            }
        }
    except (ConnectionFailure, ServerSelectionTimeoutError) as err:
        logger.error(f"[HEALTH-CHECK FAILED] Timeout / Network Failure: {err}")
        return {
            "status": "unhealthy",
            "message": f"Connection failure: {str(err)}",
            "latency_ms": None,
            "databases": {}
        }
    except PyMongoError as err:
        logger.error(f"[HEALTH-CHECK FAILED] PyMongo Exception: {err}")
        return {
            "status": "unhealthy",
            "message": f"Database exception: {str(err)}",
            "latency_ms": None,
            "databases": {}
        }
    except Exception as err:
        logger.error(f"[HEALTH-CHECK FAILED] Unexpected error: {err}")
        return {
            "status": "unhealthy",
            "message": f"Unexpected error: {str(err)}",
            "latency_ms": None,
            "databases": {}
        }


async def verify_db_connection(max_retries: int = 1, retry_delay: float = 0.5) -> Tuple[bool, str]:
    """
    Pings MongoDB Atlas with fast timeout and fallback to local storage proxy.
    """
    global use_local
    if client is None:
        use_local = True
        return False, "MongoDB client is uninitialized"

    try:
        logger.info("Connecting to MongoDB Atlas Cluster...")
        await client.admin.command('ping')
        use_local = False
        logger.info("✅ [SUCCESS] Successfully connected to MongoDB Atlas Cluster!")
        return True, "Connected to MongoDB Atlas Cloud Cluster"
    except Exception as err:
        logger.warning(f"MongoDB Atlas unreachable ({err}). Using local JSON storage fallback.")
        use_local = True
        return False, f"Using local storage fallback: {str(err)}"
import React, { createContext, useContext, useState, useEffect } from 'react';
import {
  initialKPIs,
  initialCameras,
  initialAlerts,
  initialPersonnel,
  initialWatchlist,
  initialVehicles,
  initialMissingChildren,
  initialDepotInventory,
  initialMovementLogs,
  crimeOverviewData,
  incidentsOverTimeData,
} from '../data/mockData';

const AppContext = createContext();

// --- Uniform Frontend IST Formatting Standard (Asia/Kolkata) ---
export const formatISTDate = (inputVal) => {
  if (!inputVal || inputVal === '--') return '--';
  try {
    const d = new Date(inputVal);
    if (isNaN(d.getTime())) return inputVal;
    const day = new Intl.DateTimeFormat('en-US', { day: '2-digit', timeZone: 'Asia/Kolkata' }).format(d);
    const month = new Intl.DateTimeFormat('en-US', { month: 'short', timeZone: 'Asia/Kolkata' }).format(d);
    const year = new Intl.DateTimeFormat('en-US', { year: 'numeric', timeZone: 'Asia/Kolkata' }).format(d);
    return `${day} ${month} ${year}`;
  } catch (e) {
    return inputVal;
  }
};

export const formatISTTime = (inputVal) => {
  if (!inputVal || inputVal === '--') return '--';
  try {
    const d = new Date(inputVal);
    if (isNaN(d.getTime())) return inputVal;
    const tf = new Intl.DateTimeFormat('en-US', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      hour12: true,
      timeZone: 'Asia/Kolkata'
    }).format(d);
    return `${tf} IST`;
  } catch (e) {
    return inputVal;
  }
};

const getInitialDeletedIds = () => {
  try {
    const saved = localStorage.getItem('sda_deleted_ids');
    return new Set(saved ? JSON.parse(saved) : []);
  } catch (e) {
    return new Set();
  }
};

const MOCK_IDS = new Set([
  'w-9021', 'w-9022', 'w-9023', 'w-9024', 'w-9025', 'w-4028',
  'adm-2026-001', 'adm-2026-002', 'tch-2026-202', 'tch-2026-203', 'stu-2026-101', 'stu-2026-104', 'stu-2026-105',
  'alt-101', 'alt-102', 'alt-103', 'alt-104', 'alt-105', 'alt-106', 'alt-107', 'alt-108', 'alt-109', 'alt-110',
  'alt-112', 'alt-113', 'alt-114', 'alt-115', 'alt-116', 'alt-117', 'alt-118', 'alt-119', 'alt-120', 'alt-121',
  'alt-122', 'alt-123', 'alt-124', 'alt-125', 'alt-126',
  'veh-01', 'veh-02', 'veh-03', 'veh-04', 'veh-101', 'veh-102',
  'dep-01', 'dep-02', 'dep-03', 'dep-04', 'dep-05', 'dep-06', 'arm-01', 'arm-02',
  'mov-1001', 'mov-1002', 'mc-201'
]);

const isMockItem = (id, name) => {
  if (!id && !name) return false;
  if (id && MOCK_IDS.has(String(id).trim().toLowerCase())) return true;
  if (name && (name.includes('Manoj Bajpayee') || name.includes('Shadow') || name.includes('Blade') || name.includes('Rajeshwar Deshmukh'))) return true;
  return false;
};

export const safeSetLocalStorage = (key, value) => {
  try {
    const valStr = typeof value === 'string' ? value : JSON.stringify(value);
    localStorage.setItem(key, valStr);
  } catch (e) {
    console.warn(`[localStorage] Quota limit prevented saving "${key}"`, e);
  }
};

const purgeObsoleteLocalStorage = () => {
  const obsoleteKeys = [
    'sda_personnel',
    'sda_watchlist',
    'sda_vehicles',
    'sda_missing_children',
    'sda_inventory',
    'sda_movement_logs',
    'sda_detection_reports',
    'sda_alerts',
    'sda_kpis',
    'sda_cameras',
    'sda_history_logs'
  ];
  obsoleteKeys.forEach((key) => {
    try {
      localStorage.removeItem(key);
    } catch (e) {}
  });
};

export const getAuthHeaders = () => {
  const token = localStorage.getItem('sda_token');
  const userStr = localStorage.getItem('sda_user');
  const headers = { 'Content-Type': 'application/json' };
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  if (userStr) {
    try {
      const u = JSON.parse(userStr);
      const adminId = u.admin_id || u.id || u._id;
      if (adminId) {
        headers['X-Admin-ID'] = adminId;
      }
    } catch (e) {}
  }
  return headers;
};

export const AppProvider = ({ children }) => {
  const deletedPersonnelIdsRef = React.useRef(getInitialDeletedIds());
  const isFetchingRef = React.useRef(false);

  // Authentication & Module State
  const [isAuthenticated, setIsAuthenticated] = useState(() => {
    return localStorage.getItem('sda_auth') === 'true';
  });

  const [activeModule, setActiveModule] = useState(() => {
    return localStorage.getItem('sda_active_module') || 'attendance';
  });

  const [user, setUser] = useState(() => {
    const saved = localStorage.getItem('sda_user');
    return saved ? JSON.parse(saved) : {
      name: 'Command Admin',
      role: 'Super Officer',
      badge: 'BADGE-SYS-2026',
      unit: 'Central Command & Control'
    };
  });

  // Single Source of Truth for Real Browser GPS Geolocation Tracking
  const [userLocation, setUserLocation] = useState({
    lat: null,
    lng: null,
    accuracy: null,
    isRealGps: false,
    timestamp: null,
    error: null,
    permissionState: 'prompt'
  });

  const requestGpsLocation = React.useCallback(() => {
    if (!('geolocation' in navigator)) {
      const errMsg = 'Geolocation is not supported by your browser.';
      setUserLocation(prev => ({ ...prev, isRealGps: false, error: errMsg }));
      showToast('GPS Error', errMsg, 'error');
      return;
    }

    const options = {
      enableHighAccuracy: true,
      maximumAge: 0,
      timeout: 15000
    };

    navigator.geolocation.getCurrentPosition(
      (position) => {
        const { latitude, longitude, accuracy } = position.coords;
        if (Number.isFinite(latitude) && Number.isFinite(longitude)) {
          setUserLocation({
            lat: latitude,
            lng: longitude,
            accuracy: Math.round(accuracy) || 15,
            isRealGps: true,
            timestamp: position.timestamp || Date.now(),
            error: null,
            permissionState: 'granted'
          });
          showToast('Live GPS Acquired', `Location locked: ${latitude.toFixed(4)}° N, ${longitude.toFixed(4)}° E`, 'success');
        }
      },
      (error) => {
        let msg = 'Unable to retrieve GPS location.';
        if (error.code === 1) {
          msg = 'Location permission denied by user. Please allow location access in your browser.';
        } else if (error.code === 2) {
          msg = 'GPS location position unavailable. Check your device location settings.';
        } else if (error.code === 3) {
          msg = 'GPS location request timed out.';
        }
        setUserLocation(prev => ({
          ...prev,
          isRealGps: false,
          error: msg,
          permissionState: error.code === 1 ? 'denied' : prev.permissionState
        }));
        showToast('GPS Error', msg, 'error');
      },
      options
    );
  }, []);

  useEffect(() => {
    if (!('geolocation' in navigator)) {
      setUserLocation(prev => ({
        ...prev,
        isRealGps: false,
        error: 'Geolocation is not supported by your browser.'
      }));
      return;
    }

    const options = {
      enableHighAccuracy: true,
      maximumAge: 0,
      timeout: 15000
    };

    const handleSuccess = (position) => {
      const { latitude, longitude, accuracy } = position.coords;
      if (Number.isFinite(latitude) && Number.isFinite(longitude)) {
        setUserLocation({
          lat: latitude,
          lng: longitude,
          accuracy: Math.round(accuracy) || 15,
          isRealGps: true,
          timestamp: position.timestamp || Date.now(),
          error: null,
          permissionState: 'granted'
        });
      }
    };

    const handleError = (error) => {
      let msg = 'Unable to retrieve location.';
      if (error.code === 1) {
        msg = 'Location permission denied by user. Please allow location access in browser.';
      } else if (error.code === 2) {
        msg = 'GPS location position unavailable. Check device settings.';
      } else if (error.code === 3) {
        msg = 'GPS location request timed out.';
      }

      setUserLocation(prev => ({
        ...prev,
        isRealGps: false,
        error: msg,
        permissionState: error.code === 1 ? 'denied' : prev.permissionState
      }));
    };

    const watchId = navigator.geolocation.watchPosition(handleSuccess, handleError, options);

    return () => {
      if (watchId !== null) {
        navigator.geolocation.clearWatch(watchId);
      }
    };
  }, []);

  // Registered Emergency WhatsApp & Gmail Alert Dispatch Contacts (FastAPI & MongoDB Synced)
  const [dispatchPhoneNumbers, setDispatchPhoneNumbers] = useState([]);
  const isFetchingContactsRef = React.useRef(false);

  const fetchEmergencyContacts = async () => {
    if (isFetchingContactsRef.current) return;
    isFetchingContactsRef.current = true;
    try {
      const res = await fetch('http://127.0.0.1:8000/api/settings/contacts');
      if (res.ok) {
        const data = await res.json();
        if (data.status === 'success' && Array.isArray(data.data)) {
          setDispatchPhoneNumbers(data.data.map(c => ({
            id: c.id,
            name: c.name,
            number: c.phone,
            email: c.email,
            role: c.role || 'Emergency Contact',
            is_active: c.is_active
          })));
          localStorage.setItem('sda_dispatch_numbers', JSON.stringify(data.data));
        }
      }
    } catch (e) {
      console.warn("Failed to fetch emergency contacts from backend:", e);
      const saved = localStorage.getItem('sda_dispatch_numbers');
      if (saved) {
        try {
          setDispatchPhoneNumbers(JSON.parse(saved));
        } catch (err) {}
      }
    } finally {
      isFetchingContactsRef.current = false;
    }
  };

  useEffect(() => {
    fetchEmergencyContacts();
  }, []);


  const addDispatchNumber = async (contact) => {
    if (!contact || (!contact.number && !contact.phone && !contact.email)) return;
    const rawPhone = contact.number || contact.phone || '';
    const cleanNum = rawPhone ? rawPhone.replace(/\D/g, '').slice(-10) : '';
    const formattedPhone = cleanNum ? `+91 ${cleanNum}` : (rawPhone || '+91 9876543210');
    const emailVal = contact.email ? contact.email.trim() : 'officer.command@police.gov.in';
    const nameVal = contact.name || 'Emergency Contact';
    const roleVal = contact.role || 'Duty Police Officer';

    try {
      const res = await fetch('http://127.0.0.1:8000/api/settings/contacts', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: nameVal,
          email: emailVal,
          phone: formattedPhone,
          role: roleVal,
          is_active: true
        })
      });
      const data = await res.json();
      if (data.status === 'success') {
        showToast('Emergency Contact Added', `${nameVal} saved to database & alert dispatch.`, 'success');
        fetchEmergencyContacts();
      } else {
        showToast('Error Adding Contact', data.detail || 'Failed to save contact', 'error');
      }
    } catch (e) {
      console.error("Error posting contact to backend:", e);
      // Fallback local add if server unreachable
      const newRecord = {
        id: `CONT-${Date.now()}`,
        name: nameVal,
        number: formattedPhone,
        email: emailVal,
        role: roleVal
      };
      setDispatchPhoneNumbers(prev => [newRecord, ...prev]);
      showToast('Contact Saved Locally', `${nameVal} added to local session.`, 'info');
    }
  };

  const removeDispatchNumber = async (id) => {
    if (!id) return;
    try {
      const res = await fetch(`http://127.0.0.1:8000/api/settings/contacts/${id}`, {
        method: 'DELETE'
      });
      const data = await res.json();
      if (data.status === 'success') {
        showToast('Contact Deleted', `Emergency contact removed from database.`, 'info');
        fetchEmergencyContacts();
      } else {
        setDispatchPhoneNumbers(prev => prev.filter(n => n.id !== id));
      }
    } catch (e) {
      console.error("Error deleting contact from backend:", e);
      setDispatchPhoneNumbers(prev => prev.filter(n => n.id !== id));
      showToast('Contact Removed', `Removed from active session.`, 'info');
    }
  };

  // Core Datasets (MongoDB Atlas is source of truth - in-memory state only)
  const [kpis, setKpis] = useState(initialKPIs);
  const [cameras, setCameras] = useState(initialCameras);

  const addCamera = (camData) => {
    const newCam = {
      id: camData.id || `CAM-${Date.now().toString().slice(-4)}`,
      code: camData.id || `CAM-${Date.now().toString().slice(-4)}`,
      name: camData.name || 'New Camera',
      zone: camData.location || camData.address || 'General Zone',
      location: camData.location || camData.address || 'City Grid',
      address: camData.address || camData.location || 'City Grid',
      lat: camData.lat ? parseFloat(camData.lat) : 22.7196,
      lng: camData.lng ? parseFloat(camData.lng) : 75.8577,
      status: camData.status || 'Online',
      type: camData.type || '4K Security Camera',
      resolution: '4K Ultra HD',
      lastActivity: 'Live Stream Active',
      aiDetections: 0,
      alertsCount: 0
    };
    setCameras(prev => [newCam, ...prev]);
    showToast('Camera Added', `Camera ${newCam.name} registered successfully.`, 'success');
    return newCam;
  };

  const deleteCamera = (id) => {
    setCameras(prev => prev.filter(c => c.id !== id));
    showToast('Camera Removed', `Camera ${id} has been removed.`, 'info');
  };
  const [alerts, setAlerts] = useState([]);
  const [personnel, setPersonnel] = useState([]);
  const [watchlist, setWatchlist] = useState([]);
  const [vehicles, setVehicles] = useState([]);
  const [missingChildren, setMissingChildren] = useState([]);
  const [depotInventory, setDepotInventory] = useState([]);
  const [movementLogs, setMovementLogs] = useState([]);
  const [detectionReports, setDetectionReports] = useState([]);
  const [historyLogs, setHistoryLogs] = useState([]);

  const addHistoryLog = (logItem) => {
    const nowObj = new Date();
    const dFormatted = formatISTDate(nowObj);
    const tFormatted = formatISTTime(nowObj);
    const newLog = {
      id: logItem.id || `HIST-${Date.now()}-${Math.floor(Math.random() * 1000)}`,
      personId: logItem.personId || logItem.id || '--',
      name: logItem.name || 'Unknown',
      role: logItem.role || 'Personnel',
      department: logItem.department || 'General Branch',
      action: logItem.action || 'Attendance Check-in',
      status: logItem.status || 'Present',
      dateTime: logItem.dateTime || `${dFormatted}, ${tFormatted}`,
      timestamp: logItem.timestamp || nowObj.toISOString(),
      details: logItem.details || 'Event recorded in system audit history'
    };
    setHistoryLogs(prev => [newLog, ...prev]);
  };

  const deleteHistoryLog = (id) => {
    if (!id) return;
    setHistoryLogs(prev => prev.filter(h => h.id !== id));
    showToast('History Entry Removed', `History record ${id} has been deleted.`, 'info');
  };

  const deleteMultipleHistoryLogs = (ids = []) => {
    if (!ids || ids.length === 0) return;
    const cleanSet = new Set(ids.map(i => String(i)));
    setHistoryLogs(prev => prev.filter(h => !cleanSet.has(String(h.id))));
    showToast('Batch History Deleted', `Removed ${ids.length} entry/entries from audit history archive.`, 'success');
  };

  const clearAllHistoryLogs = () => {
    setHistoryLogs([]);
    showToast('Audit History Cleared', 'All audit history records have been removed.', 'info');
  };

  // Global UI States, Modals & Theme
  const [theme, setTheme] = useState(() => {
    return localStorage.getItem('sda_theme') || 'light';
  });

  const toggleTheme = () => {
    setTheme(prev => (prev === 'light' ? 'dark' : 'light'));
  };

  useEffect(() => {
    safeSetLocalStorage('sda_theme', theme);
    if (theme === 'dark') {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [theme]);

  const [globalSearch, setGlobalSearch] = useState('');
  const [selectedCameraForModal, setSelectedCameraForModal] = useState(null);
  const [activeModal, setActiveModal] = useState(null); // 'addAlert', 'searchPerson', 'searchVehicle', 'generateReport', 'addPerson', 'addWatchlist', 'addMissingChild'
  const [toastMessage, setToastMessage] = useState(null);

  // Sync small session preference to LocalStorage safely
  useEffect(() => {
    safeSetLocalStorage('sda_auth', String(isAuthenticated));
  }, [isAuthenticated]);

  // 🕒 Current Shift Date Engine (Without Midnight Data Reset)
  const [currentShiftDate, setCurrentShiftDate] = useState(() => new Date().toISOString().slice(0, 10));

  useEffect(() => {
    const timer = setInterval(() => {
      const nowStr = new Date().toISOString().slice(0, 10);
      if (nowStr !== currentShiftDate) {
        console.log(`[Shift Date Engine] Date Transition: ${currentShiftDate} -> ${nowStr}`);
        setCurrentShiftDate(nowStr);
        window.dispatchEvent(new CustomEvent('chakravyuh_shift_date_change', { detail: { date: nowStr } }));
      }
    }, 1000);
    return () => clearInterval(timer);
  }, [currentShiftDate]);

  // ⚡ One-Time Initial Load from MongoDB Atlas on Startup (ZERO Automatic Background Continuous Polling)
  const abortControllerRef = React.useRef(null);

  useEffect(() => {
    // Purge obsolete large keys from localStorage to prevent QuotaExceededError permanently
    purgeObsoleteLocalStorage();

    let isMounted = true;

    const fetchInitialModuleData = async () => {
      if (isFetchingRef.current) return;
      isFetchingRef.current = true;

      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
      const controller = new AbortController();
      abortControllerRef.current = controller;

      const authHeaders = getAuthHeaders();
      const userStr = localStorage.getItem('sda_user');
      let currentAdminId = user?.admin_id || user?.id || user?._id || '';
      if (!currentAdminId && userStr) {
        try {
          const u = JSON.parse(userStr);
          currentAdminId = u.admin_id || u.id || u._id || '';
        } catch (e) {}
      }
      const q = currentAdminId ? `?admin_id=${encodeURIComponent(currentAdminId)}` : '';

      try {
        const [
          personnelRes,
          watchlistRes,
          vehiclesRes,
          missingRes,
          inventoryRes
        ] = await Promise.allSettled([
          fetch(`http://127.0.0.1:8000/api/attendance/personnel${q}`, { headers: authHeaders, signal: controller.signal }),
          fetch(`http://127.0.0.1:8000/api/criminal/watchlist${q}`, { headers: authHeaders, signal: controller.signal }),
          fetch(`http://127.0.0.1:8000/api/anpr/vehicles${q}`, { headers: authHeaders, signal: controller.signal }),
          fetch(`http://127.0.0.1:8000/api/missing-children/records${q}`, { headers: authHeaders, signal: controller.signal }),
          fetch(`http://127.0.0.1:8000/api/defence/inventory${q}`, { headers: authHeaders, signal: controller.signal })
        ]);

        if (!isMounted || controller.signal.aborted) return;

        // 1. Attendance personnel (registered_data)
        if (personnelRes.status === 'fulfilled' && personnelRes.value.ok) {
          try {
            const json = await personnelRes.value.json();
            if (json.status === 'success' && Array.isArray(json.data) && isMounted) {
              const validDocs = json.data.filter(d => 
                d && d.id && 
                !deletedPersonnelIdsRef.current.has(String(d.id).trim().toLowerCase()) &&
                d.id !== 'STU-E2E-999' &&
                d.name !== 'Frontend E2E Student' &&
                d.name !== 'Test Student Verification'
              );
              setPersonnel(validDocs);
            }
          } catch (e) {}
        }

        // 2. Criminal Watchlist (registered_data)
        if (watchlistRes.status === 'fulfilled' && watchlistRes.value.ok) {
          try {
            const json = await watchlistRes.value.json();
            if (json.status === 'success' && Array.isArray(json.data) && isMounted) {
              setWatchlist(json.data);
            }
          } catch (e) {}
        }

        // 3. ANPR Vehicles (registered_data)
        if (vehiclesRes.status === 'fulfilled' && vehiclesRes.value.ok) {
          try {
            const json = await vehiclesRes.value.json();
            if (json.status === 'success' && Array.isArray(json.data) && isMounted) {
              setVehicles(json.data);
            }
          } catch (e) {}
        }

        // 4. Missing Children (registered_data)
        if (missingRes.status === 'fulfilled' && missingRes.value.ok) {
          try {
            const json = await missingRes.value.json();
            if (json.status === 'success' && Array.isArray(json.data) && isMounted) {
              setMissingChildren(json.data);
            }
          } catch (e) {}
        }

        // 5. Defence Armory Inventory (registered_data)
        if (inventoryRes.status === 'fulfilled' && inventoryRes.value.ok) {
          try {
            const json = await inventoryRes.value.json();
            if (json.status === 'success' && Array.isArray(json.data) && isMounted) {
              setDepotInventory(json.data);
            }
          } catch (e) {}
        }
      } catch (e) {
        if (e.name !== 'AbortError') {
          console.warn("[Initial Fetch] Backend notice:", e);
        }
      } finally {
        isFetchingRef.current = false;
      }
    };

    fetchInitialModuleData();

    return () => {
      isMounted = false;
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
        abortControllerRef.current = null;
      }
    };
  }, [isAuthenticated, user?.admin_id, user?.id, user?._id]);

  // Toast Notification helper
  const showToast = (title, message, type = 'info') => {
    setToastMessage({ title, message, type, id: Date.now() });
    setTimeout(() => setToastMessage(null), 4000);
  };

  // Auth Handlers
  const loginModule = (moduleId, userData) => {
    setIsAuthenticated(true);
    setActiveModule(moduleId);
    const updatedUser = {
      name: userData?.name || 'Officer Admin',
      role: userData?.role || 'Command Officer',
      badge: userData?.badge || `BADGE-${moduleId.toUpperCase()}-2026`,
      unit: `${moduleId.toUpperCase()} Command Division`
    };
    setUser(updatedUser);
    localStorage.setItem('sda_auth', 'true');
    localStorage.setItem('sda_active_module', moduleId);
    localStorage.setItem('sda_user', JSON.stringify(updatedUser));
  };

  const login = (role = 'Super Admin') => {
    setIsAuthenticated(true);
    setUser(prev => ({ ...prev, role }));
    showToast('Authenticated', 'Access granted to Command & Control Hub', 'success');
  };

  const logout = () => {
    setIsAuthenticated(false);
    setUser(null);
    setPersonnel([]);
    setWatchlist([]);
    setVehicles([]);
    setMissingChildren([]);
    setDepotInventory([]);
    localStorage.removeItem('sda_auth');
    localStorage.removeItem('sda_token');
    localStorage.removeItem('sda_user');
    localStorage.removeItem('sda_active_module');
    showToast('Logged Out', 'Admin session terminated successfully', 'info');
  };

  // ---------------------------------------------------------
  // 1. ATTENDANCE MODULE HANDLERS
  // ---------------------------------------------------------
  const addPerson = async (newPerson) => {
    const adminId = user?.admin_id || user?.id || user?._id || '';
    const person = {
      id: newPerson.id || `EMP-${Math.floor(1000 + Math.random() * 9000)}`,
      module: newPerson.module || activeModule || 'attendance',
      name: newPerson.name,
      department: newPerson.department || 'Security',
      role: newPerson.role || 'Officer',
      entry: newPerson.entry || '--',
      exit: '--',
      status: newPerson.status || 'Registered',
      camera: newPerson.camera || 'CAM-01',
      avatar: newPerson.avatar || '👤',
      photoUrl: newPerson.photoUrl || null,
      badgeId: `BADGE-${Math.floor(1000 + Math.random() * 9000)}`,
      admin_id: adminId
    };

    try {
      const res = await fetch('http://127.0.0.1:8000/api/attendance/personnel', {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify(person)
      });
      const data = await res.json();
      if (res.ok && (data.status === 'success' || data._id)) {
        setPersonnel(prev => [person, ...prev.filter(p => p.id !== person.id)]);
        addHistoryLog({
          personId: person.id,
          name: person.name,
          role: person.role,
          department: person.department,
          action: 'Personnel Registered',
          status: 'Registered',
          details: `Registered profile saved to MongoDB Atlas`
        });
        showToast('Personnel Registered', `${person.name} (${person.id}) saved to MongoDB Atlas.`, 'success');
        return { success: true, data: person };
      } else {
        throw new Error(data.detail || data.message || 'Server rejected registration');
      }
    } catch (e) {
      console.error('MongoDB person registration error:', e);
      showToast('Registration Error', `Failed to register ${person.name}: ${e.message}`, 'error');
      return { success: false, error: e.message };
    }
  };

  const deletePersonnel = async (id) => {
    if (!id) return;
    let deletedName = id;
    const cleanId = String(id).trim().toLowerCase();
    deletedPersonnelIdsRef.current.add(cleanId);

    try {
      const res = await fetch(`http://127.0.0.1:8000/api/attendance/personnel/${encodeURIComponent(id)}`, {
        method: 'DELETE'
      });
      const data = await res.json();
      if (res.ok) {
        setPersonnel(prev => prev.filter(p => String(p.id).trim().toLowerCase() !== cleanId));
        showToast('Record Deleted', `Record ${id} permanently removed from MongoDB Atlas.`, 'info');
      } else {
        throw new Error(data.detail || 'Delete failed on server');
      }
    } catch (e) {
      console.error('Backend DELETE API exception:', e);
      showToast('Delete Error', `Could not delete ${id}: ${e.message}`, 'error');
    }
  };

  const deleteMultiplePersonnel = async (ids = []) => {
    if (!ids || ids.length === 0) return;
    ids.forEach(i => deletedPersonnelIdsRef.current.add(String(i).trim().toLowerCase()));

    try {
      const res = await fetch('http://127.0.0.1:8000/api/attendance/personnel/delete-batch', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ids })
      });
      const data = await res.json();
      if (res.ok) {
        const cleanSet = new Set(ids.map(i => String(i).trim().toLowerCase()));
        setPersonnel(prev => prev.filter(p => !cleanSet.has(String(p.id).trim().toLowerCase())));
        showToast('Batch Delete Completed', `Deleted ${ids.length} record(s) from MongoDB Atlas.`, 'success');
      } else {
        throw new Error(data.detail || 'Batch delete failed');
      }
    } catch (e) {
      console.error('Backend delete-batch API exception:', e);
      showToast('Delete Error', `Batch delete failed: ${e.message}`, 'error');
    }
  };

  const markAttendance = async (empId, status = 'Present', options = {}) => {
    const targetPerson = personnel.find(p => p.id === empId || p.name === empId);
    const markedName = targetPerson ? targetPerson.name : empId;
    const nowObj = new Date();
    const todayShiftDate = nowObj.toISOString().slice(0, 10);
    const dateStr = options.date || todayShiftDate;

    try {
      const res = await fetch('http://127.0.0.1:8000/api/attendance/mark', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          id: empId,
          name: markedName,
          role: targetPerson?.role || 'Student',
          department: targetPerson?.department || 'General Branch / Department',
          avatar: targetPerson?.avatar || '👤',
          photoUrl: targetPerson?.photoUrl || null,
          status,
          date: dateStr
        })
      });
      const data = await res.json();
      if (data.status === 'cooldown' || data.success === false) {
        if (!options.silent) {
          showToast(
            'Already Scanned',
            `Attendance already recorded. Next attendance available after: ${data.next_allowed_at || '20 hours'}`,
            'warning'
          );
        }
        return { 
          success: false, 
          status: 'cooldown', 
          message: data.message || 'Attendance already recorded. Try again after 20 hours.', 
          next_allowed_at: data.next_allowed_at 
        };
      }

      if (res.ok && (data.status === 'success' || data.status === 'accepted' || data.success === true)) {
        const serverTime = data.server_time || {};
        setPersonnel(prev => prev.map(p => {
          if (p.id === empId || p.name === empId) {
            return {
              ...p,
              status,
              entry: (status === 'Present' || status === 'Late') ? serverTime.full_datetime || new Date().toLocaleString() : '--'
            };
          }
          return p;
        }));
        if (!options.silent) {
          showToast('Attendance Logged', `Attendance marked as ${status} for ${markedName} in MongoDB Atlas`, 'success');
        }
        return { success: true, next_allowed_at: data.next_allowed_at };
      } else {
        throw new Error(data.detail || data.message || 'Failed to mark attendance');
      }
    } catch (e) {
      console.error('MongoDB sync error:', e);
      if (!options.silent) {
        showToast('Attendance Error', `Could not mark attendance: ${e.message}`, 'error');
      }
      return { success: false, error: e.message };
    }
  };

  const addAttendanceScan = async (scanData) => {
    try {
      await fetch('http://127.0.0.1:8000/api/attendance/attendance_scan', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...scanData,
          created_at: new Date().toISOString()
        })
      });
    } catch (e) {
      console.error('Error saving attendance scan to MongoDB:', e);
    }
  };

  // ---------------------------------------------------------
  // 2. CRIMINAL TRACKING MODULE HANDLERS
  // ---------------------------------------------------------
  const addToWatchlist = async (item) => {
    const adminId = user?.admin_id || user?.id || user?._id || '';
    const record = {
      id: item.id || `W-${Math.floor(9000 + Math.random() * 999)}`,
      module: item.module || activeModule || 'criminal-tracking',
      name: item.name,
      riskLevel: item.riskLevel || 'High Risk',
      crimeType: item.crimeType || item.charges || item.details || 'Under Watchlist Surveillance',
      charges: item.charges || item.ipcCharges || item.crimeType || 'IPC 302 / 395 - Armed Robbery & Homicide',
      lastSeen: item.lastSeen || item.location || 'CAM-01 Primary Station',
      status: item.status || 'REGISTERED & ACTIVE',
      confidence: item.confidence || '98.5%',
      photoUrl: item.photoUrl || item.photo || null,
      age: item.age || 32,
      details: item.details || item.crimeType || 'Registered into criminal watchlist.',
      admin_id: adminId
    };

    try {
      const res = await fetch('http://127.0.0.1:8000/api/criminal/watchlist', {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify(record)
      });
      const data = await res.json();
      if (res.ok && (data.status === 'success' || data._id)) {
        setWatchlist(prev => [record, ...prev.filter(w => w.id !== record.id)]);
        showToast('Target Registered', `${record.name} saved to MongoDB Atlas watchlist.`, 'success');
        return { success: true, data: record };
      } else {
        throw new Error(data.detail || 'Failed to save suspect');
      }
    } catch (e) {
      console.error("MongoDB criminal sync notice:", e);
      showToast('Registration Error', `Failed to register suspect: ${e.message}`, 'error');
      return { success: false, error: e.message };
    }
  };

  const removeFromWatchlist = async (id) => {
    if (!id) return;
    try {
      const res = await fetch(`http://127.0.0.1:8000/api/criminal/watchlist/${encodeURIComponent(id)}`, {
        method: 'DELETE'
      });
      if (res.ok) {
        setWatchlist(prev => prev.filter(w => w.id !== id));
        showToast('Profile Removed', `Watchlist record ${id} removed from MongoDB Atlas.`, 'info');
      }
    } catch (e) {
      console.error('Error removing suspect from MongoDB:', e);
    }
  };

  const deleteMultipleWatchlist = async (ids = []) => {
    if (!ids || ids.length === 0) return;
    for (const id of ids) {
      await removeFromWatchlist(id);
    }
    showToast('Batch Profiles Removed', `Removed ${ids.length} suspect records from MongoDB Atlas.`, 'info');
  };

  const addCriminalDetection = async (detectionData) => {
    try {
      await fetch('http://127.0.0.1:8000/api/criminal/criminal_detections', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...detectionData,
          created_at: new Date().toISOString()
        })
      });
    } catch (e) {
      console.error('Error saving criminal detection to MongoDB:', e);
    }
  };

  const clearCustomWatchlist = () => {
    setWatchlist(prev => prev.filter(w => !w.isUserAdded));
    showToast('Custom Profiles Cleared', 'All custom user-registered profiles removed.', 'info');
  };

  const resetWatchlist = () => {
    localStorage.removeItem('sda_watchlist');
    setWatchlist(initialWatchlist);
    showToast('Watchlist Reset', 'Watchlist database reset to initial state.', 'info');
  };

  // Alert Handlers
  const addAlert = async (alertData) => {
    if (alertData.type?.includes('Attendance Check-in') || alertData.title?.includes('ATTENDANCE MARKED')) {
      return;
    }
    const fullText = `${alertData.title || ''} ${alertData.type || ''} ${alertData.description || ''}`.toLowerCase();
    let mod = alertData.module;

    if (!mod || fullText.includes('watchlist') || fullText.includes('criminal') || fullText.includes('suspect') || fullText.includes('fugitive') || fullText.includes('ipc')) {
      if (fullText.includes('watchlist') || fullText.includes('criminal') || fullText.includes('suspect') || fullText.includes('fugitive') || fullText.includes('ipc')) {
        mod = 'criminal-tracking';
      } else if (fullText.includes('case mc-') || fullText.includes('missing') || fullText.includes('child')) {
        mod = 'missing-child';
      } else if (fullText.includes('breach') || fullText.includes('armory') || fullText.includes('vault') || fullText.includes('perimeter') || fullText.includes('defence') || fullText.includes('defense')) {
        mod = 'defence';
      } else if (fullText.includes('anpr') || fullText.includes('speed') || fullText.includes('vehicle')) {
        mod = 'anpr';
      } else {
        mod = alertData.module || activeModule || 'criminal-tracking';
      }
    }

    const newAlert = {
      id: alertData.id || `ALT-${Math.floor(200 + Math.random() * 800)}`,
      module: mod,
      type: alertData.type || 'Custom Incident Alert',
      title: alertData.title || alertData.type,
      location: alertData.location || 'Central Sector',
      camera: alertData.camera || 'CAM-01',
      priority: alertData.priority || 'High',
      timeAgo: 'Just now',
      description: alertData.description || 'Reported manual alert via Command Console.',
      status: 'Active',
      icon: alertData.priority === 'Critical' ? 'Shield' : 'AlertTriangle',
      badgeColor: alertData.priority === 'Critical' ? 'border-red-500/50 text-red-400' : 'border-teal-500/40 text-teal-400'
    };
    setAlerts(prev => [newAlert, ...prev]);

    let alertUrl = 'http://127.0.0.1:8000/api/criminal/alerts';
    if (mod === 'missing-child' || mod === 'missing') alertUrl = 'http://127.0.0.1:8000/api/missing-children/alerts';
    else if (mod === 'attendance') alertUrl = 'http://127.0.0.1:8000/api/attendance/alerts';
    else if (mod === 'anpr') alertUrl = 'http://127.0.0.1:8000/api/anpr/alerts';
    else if (mod === 'defence') alertUrl = 'http://127.0.0.1:8000/api/defence/alerts';

    try {
      await fetch(alertUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newAlert)
      });
    } catch (e) {}

    showToast('Alert Dispatched', `${newAlert.title} broadcasted to active units.`, 'warning');
  };

  const acknowledgeAlert = (id) => {
    setAlerts(prev => prev.map(a => a.id === id ? { ...a, status: 'Acknowledged' } : a));
    showToast('Alert Acknowledged', `Incident ${id} acknowledged by Command.`, 'info');
  };

  const resolveAlert = (id) => {
    setAlerts(prev => prev.map(a => a.id === id ? { ...a, status: 'Resolved' } : a));
    showToast('Alert Resolved', `Incident ${id} marked as resolved.`, 'success');
  };

  const deleteAlert = async (id) => {
    setAlerts(prev => prev.filter(a => a.id !== id));
    try {
      await fetch(`http://127.0.0.1:8000/api/criminal/alerts/${encodeURIComponent(id)}`, { method: 'DELETE' });
    } catch (e) {}
    showToast('Alert Deleted', `Alert ${id} permanently removed.`, 'info');
  };

  const deleteMultipleAlerts = (idsArray) => {
    if (!idsArray || idsArray.length === 0) return;
    setAlerts(prev => prev.filter(a => !idsArray.includes(a.id)));
    showToast('Alerts Deleted', `${idsArray.length} alert(s) permanently removed.`, 'info');
  };

  const clearAllAlerts = () => {
    setAlerts([]);
    showToast('All Alerts Cleared', 'All alerts permanently removed.', 'info');
  };

  // ---------------------------------------------------------
  // 3. ANPR MODULE HANDLERS
  // ---------------------------------------------------------
  const addVehicleRecord = async (veh) => {
    const adminId = user?.admin_id || user?.id || user?._id || '';
    const record = {
      id: veh.id || `VEH-${Math.floor(1000 + Math.random() * 9000)}`,
      module: veh.module || activeModule || 'anpr',
      plate: veh.plate,
      type: veh.type || 'Sedan / SUV',
      owner: veh.owner || 'Registered Owner',
      status: veh.status || 'Authorized',
      confidence: veh.confidence || '98.5%',
      lastLocation: veh.lastLocation || 'Highway Toll Gate',
      admin_id: adminId
    };

    try {
      const res = await fetch('http://127.0.0.1:8000/api/anpr/vehicles', {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify(record)
      });
      const data = await res.json();
      if (res.ok && (data.status === 'success' || data._id)) {
        setVehicles(prev => [record, ...prev.filter(v => v.id !== record.id)]);
        showToast('ANPR Logged', `Vehicle ${veh.plate} saved to MongoDB Atlas.`, 'success');
        return { success: true, data: record };
      } else {
        throw new Error(data.detail || 'Failed to save vehicle');
      }
    } catch (e) {
      console.error('Error saving vehicle to MongoDB:', e);
      showToast('ANPR Save Error', `Could not save vehicle: ${e.message}`, 'error');
      return { success: false, error: e.message };
    }
  };

  const addAnprScan = async (scanData) => {
    try {
      await fetch('http://127.0.0.1:8000/api/anpr/anpr_scan', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...scanData,
          created_at: new Date().toISOString()
        })
      });
    } catch (e) {
      console.error('Error saving ANPR scan to MongoDB:', e);
    }
  };

  // ---------------------------------------------------------
  // 4. MISSING CHILDREN MODULE HANDLERS
  // ---------------------------------------------------------
  const addMissingChild = async (childData) => {
    const adminId = user?.admin_id || user?.id || user?._id || '';
    const newCase = {
      id: childData.id || `MC-2026-${String(Math.floor(100 + Math.random() * 900))}`,
      module: childData.module || activeModule || 'missing-child',
      name: childData.name,
      age: parseInt(childData.age) || 6,
      gender: childData.gender || 'Male',
      guardianName: childData.guardianName || childData.fatherName || 'Parent / Guardian',
      contactNumber: childData.contactNumber || childData.phone || '+91 9876543210',
      address: childData.address || 'Central District',
      missingDate: childData.missingDate || new Date().toISOString().slice(0, 10),
      lastSeenLocation: childData.lastSeenLocation || childData.missingLocation || 'Central District',
      description: childData.description || 'No description provided.',
      photoUrl: childData.photoUrl || '',
      embedding: childData.embedding || null,
      status: 'Searching',
      lat: childData.lat || 22.7250,
      lng: childData.lng || 75.8600,
      admin_id: adminId
    };

    try {
      const res = await fetch('http://127.0.0.1:8000/api/missing-children/records', {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify(newCase)
      });
      const data = await res.json();
      if (res.ok && (data.status === 'success' || data._id)) {
        setMissingChildren(prev => [newCase, ...prev.filter(m => m.id !== newCase.id)]);

        // Save metadata to Missing_children.add_data collection
        try {
          await fetch('http://127.0.0.1:8000/api/missing-children/add_data', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              case_id: newCase.id,
              child_name: newCase.name,
              guardian_name: newCase.guardianName,
              contact_number: newCase.contactNumber,
              address: newCase.address,
              missing_date: newCase.missingDate,
              missing_location: newCase.lastSeenLocation,
              description: newCase.description,
              created_at: new Date().toISOString()
            })
          });
        } catch (err) {}

        showToast('Case Registered', `Missing person case ${newCase.id} saved to MongoDB Atlas.`, 'success');
        return { success: true, data: newCase };
      } else {
        throw new Error(data.detail || 'Failed to save missing child case');
      }
    } catch (e) {
      console.error('Error saving missing child case to MongoDB:', e);
      showToast('Registration Error', `Could not save case: ${e.message}`, 'error');
      return { success: false, error: e.message };
    }
  };

  const deleteMissingChild = async (id) => {
    if (!id) return;
    try {
      const res = await fetch(`http://127.0.0.1:8000/api/missing-children/records/${encodeURIComponent(id)}`, {
        method: 'DELETE'
      });
      if (res.ok) {
        setMissingChildren(prev => prev.filter(c => c.id !== id));
        showToast('Case Removed', `Missing child case ${id} removed from MongoDB Atlas.`, 'info');
      }
    } catch (e) {
      console.error('Error deleting missing child case:', e);
    }
  };

  const addDetectionReport = async (childData, confidence, location) => {
    const newReport = {
      id: `RPT-${Math.floor(10000 + Math.random() * 90000)}`,
      childId: childData.id,
      childName: childData.name,
      age: childData.age,
      gender: childData.gender,
      matchConfidence: String(confidence),
      detectedLocation: location || childData.lastSeenLocation,
      timestamp: new Date().toLocaleString(),
      photoUrl: childData.photoUrl,
      status: 'LOCATED & VERIFIED'
    };
    setDetectionReports(prev => [newReport, ...prev]);

    // Persist scan detection to children_detection collection
    try {
      await fetch('http://127.0.0.1:8000/api/missing-children/children_detection', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          childId: childData.id,
          childName: childData.name,
          confidence: String(confidence),
          location: location || childData.lastSeenLocation,
          created_at: new Date().toISOString()
        })
      });
    } catch (e) {
      console.error('Error saving missing child detection to MongoDB:', e);
    }

    showToast('Detection Report Generated', `Match confirmed: ${childData.name} saved to MongoDB Atlas`, 'success');
  };

  // ---------------------------------------------------------
  // 5. DEFENCE TACTICAL MODULE HANDLERS
  // ---------------------------------------------------------
  const updateDepotMovement = async (itemId, type, quantityChange) => {
    const timeNow = new Date().toTimeString().slice(0, 5);
    setDepotInventory(prev => prev.map(item => {
      if (item.id === itemId || item.item?.includes(itemId)) {
        const newQty = Math.max(0, item.quantity + quantityChange);
        return { ...item, quantity: newQty, lastChecked: 'Just now (Verified Movement)' };
      }
      return item;
    }));

    const logDoc = {
      id: `MOV-${Math.floor(2000 + Math.random() * 8000)}`,
      time: timeNow,
      item: itemId,
      type: type || 'Authorized Transfer',
      officer: `${user.name} (${user.badge})`,
      status: 'Logged & Verified',
      zone: 'Depot A - Main Gate'
    };
    setMovementLogs(prev => [logDoc, ...prev]);

    // Persist scan/movement to defence_scan collection
    try {
      await fetch('http://127.0.0.1:8000/api/defence/defence_scan', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(logDoc)
      });
    } catch (e) {
      console.error('Error saving defence scan to MongoDB:', e);
    }

    showToast('Movement Logged', `Transfer of ${itemId} recorded in MongoDB Atlas.`, 'success');
  };

  const addDefenceScan = async (scanData) => {
    try {
      await fetch('http://127.0.0.1:8000/api/defence/defence_scan', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...scanData,
          created_at: new Date().toISOString()
        })
      });
    } catch (e) {
      console.error('Error saving defence scan to MongoDB:', e);
    }
  };

  const triggerMovementBreach = (zone, details) => {
    const alertItem = {
      type: 'Perimeter Breach',
      title: 'UNAUTHORIZED MOVEMENT DETECTED',
      location: zone || 'Defense Zone 3',
      camera: 'CAM-06',
      priority: 'Critical',
      description: details || 'Sensors tripped at Armory Vault. Thermal perimeter breach confirmed.'
    };
    addAlert(alertItem);
  };

  const deleteDepotItem = async (id) => {
    setDepotInventory(prev => prev.filter(item => item.id !== id));
    try {
      await fetch(`http://127.0.0.1:8000/api/defence/inventory/${encodeURIComponent(id)}`, {
        method: 'DELETE'
      });
      await fetch(`http://127.0.0.1:8000/api/defence/registered_data/${encodeURIComponent(id)}`, {
        method: 'DELETE'
      });
    } catch (e) {}
    showToast('Item Deleted', `Inventory asset ${id} removed from Defence database.`, 'info');
  };


  const addReport = async (reportData = {}) => {
    const mod = reportData.module || activeModule || 'attendance';
    const reportDoc = {
      id: reportData.id || `RPT-${Date.now()}-${Math.floor(Math.random() * 1000)}`,
      module: mod,
      title: reportData.title || 'Generated System Audit Report',
      format: reportData.format || 'pdf',
      dateRange: reportData.dateRange || 'current-week',
      created_at: new Date().toISOString()
    };

    let targetUrl = 'http://127.0.0.1:8000/api/attendance/reports';
    if (mod === 'criminal-tracking' || mod === 'criminal') targetUrl = 'http://127.0.0.1:8000/api/criminal/reports';
    else if (mod === 'anpr') targetUrl = 'http://127.0.0.1:8000/api/anpr/reports';
    else if (mod === 'missing-child' || mod === 'missing') targetUrl = 'http://127.0.0.1:8000/api/missing-children/reports';
    else if (mod === 'defence') targetUrl = 'http://127.0.0.1:8000/api/defence/reports';

    try {
      await fetch(targetUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(reportDoc)
      });
    } catch (e) {
      console.error('Error saving report to MongoDB:', e);
    }
  };

  const saveSystemSettings = async (settingsData = {}) => {
    const mod = activeModule || 'attendance';
    const settingsDoc = {
      id: `SETTINGS-${mod.toUpperCase()}`,
      module: mod,
      settings: settingsData,
      updated_at: new Date().toISOString()
    };

    let targetUrl = 'http://127.0.0.1:8000/api/attendance/system_settings';
    if (mod === 'criminal-tracking' || mod === 'criminal') targetUrl = 'http://127.0.0.1:8000/api/criminal/system_settings';
    else if (mod === 'anpr') targetUrl = 'http://127.0.0.1:8000/api/anpr/system_setting';
    else if (mod === 'missing-child' || mod === 'missing') targetUrl = 'http://127.0.0.1:8000/api/missing-children/system_setting';
    else if (mod === 'defence') targetUrl = 'http://127.0.0.1:8000/api/defence/system_setting';

    try {
      await fetch(targetUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(settingsDoc)
      });
      showToast('Settings Saved', `System preferences saved to MongoDB Atlas.`, 'success');
    } catch (e) {
      console.error('Error saving settings to MongoDB:', e);
    }
  };

  // Camera Management
  const toggleCameraStatus = async (id) => {
    let nextStatus = 'Online';
    setCameras(prev => prev.map(c => {
      if (c.id === id) {
        nextStatus = c.status === 'Online' ? 'Offline' : 'Online';
        showToast('Camera Status Changed', `${c.id} (${c.name}) is now ${nextStatus}`, 'info');
        return { ...c, status: nextStatus };
      }
      return c;
    }));

    try {
      await fetch('http://127.0.0.1:8000/api/attendance/camera_network', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id, status: nextStatus, updated_at: new Date().toISOString() })
      });
    } catch (e) {}
  };

  // Sidebar Collapsed State
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);
  const toggleSidebar = () => setIsSidebarCollapsed(prev => !prev);

  // Dynamic Real-Time Calculated KPIs from actual state
  const calculatedKPIs = {
    totalPersonnel: { value: String(personnel.length), label: 'Total Person', subtext: 'Registered Officers' },
    activeCameras: { value: '1', label: 'Active Camera', subtext: 'Live Desktop Webcam' },
    activeAlerts: { value: String(alerts.filter(a => a.status === 'Active').length), label: 'Active Alerts', subtext: 'Live Triage' },
    criminalsTracked: { value: String(watchlist.length), label: 'Criminals Tracked', subtext: 'Watchlist Suspects' },
    missingChildren: { value: String(missingChildren.filter(m => m.status === 'Missing').length), label: 'Missing Children', subtext: 'Active Cases' },
  };

  return (
    <AppContext.Provider
      value={{
        isAuthenticated,
        activeModule,
        setActiveModule,
        loginModule,
        user,
        kpis: calculatedKPIs,
        calculatedKPIs,
        cameras,
        setCameras,
        addCamera,
        deleteCamera,
        alerts,
        personnel,
        watchlist,
        vehicles,
        missingChildren,
        depotInventory,
        movementLogs,
        detectionReports,
        historyLogs,
        addHistoryLog,
        deleteHistoryLog,
        deleteMultipleHistoryLogs,
        clearAllHistoryLogs,
        crimeOverviewData,
        incidentsOverTimeData,
        theme,
        setTheme,
        toggleTheme,
        isSidebarCollapsed,
        setIsSidebarCollapsed,
        toggleSidebar,
        globalSearch,
        setGlobalSearch,
        selectedCameraForModal,
        setSelectedCameraForModal,
        activeModal,
        setActiveModal,
        toastMessage,
        showToast,
        login,
        logout,
        addPerson,
        deletePersonnel,
        deleteMultiplePersonnel,
        markAttendance,
        addToWatchlist,
        removeFromWatchlist,
        deleteMultipleWatchlist,
        clearCustomWatchlist,
        resetWatchlist,
        addAlert,
        acknowledgeAlert,
        resolveAlert,
        deleteAlert,
        deleteMultipleAlerts,
        clearAllAlerts,
        addMissingChild,
        deleteMissingChild,
        addDetectionReport,
        addVehicleRecord,
        addAnprScan,
        addAttendanceScan,
        addCriminalDetection,
        addDefenceScan,
        addReport,
        saveSystemSettings,
        updateDepotMovement,
        triggerMovementBreach,
        deleteDepotItem,
        toggleCameraStatus,
        dispatchPhoneNumbers,
        addDispatchNumber,
        removeDispatchNumber,
        userLocation,
        setUserLocation,
        requestGpsLocation
      }}
    >
      {children}
    </AppContext.Provider>
  );
};

export const useApp = () => useContext(AppContext);

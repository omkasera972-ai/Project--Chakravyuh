 🛡️ PROJECT CHAKRAVYUH v2.0

> **Enterprise Multi-Purpose AI Security, Biometric Surveillance & Tactical Intelligence Command Platform**

[![React](https://img.shields.io/badge/React-18.3.1-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://react.dev/)
[![Vite](https://img.shields.io/badge/Vite-5.4.14-646CFF?style=for-the-badge&logo=vite&logoColor=white)](https://vitejs.dev/)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-3.4.17-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white)](https://tailwindcss.com/)
[![Face-API](https://img.shields.io/badge/AI_Engine-ResNet34_128D-FF6F00?style=for-the-badge&logo=tensorflow&logoColor=white)](https://github.com/vladmandic/face-api)

---

## 📌 Executive Summary

**Project Chakravyuh v2.0** is a next-generation **AI-Powered Tactical Security & Biometric Surveillance System** designed for high-security multi-domain environments. It integrates real-time computer vision, deep-learning facial recognition (ResNet-34 128-D Biometric Embeddings), automatic license plate recognition (ANPR), missing children rescue radar, and military-grade perimeter defense under a unified, reactive control center.

---

## 🏛️ System Architecture

```text
                               ┌─────────────────────────────────────────────────┐
                               │         CHAKRAVYUH PURPOSE SELECTOR             │
                               │   (Multi-Domain Operational Security Gateway)   │
                               └───────────────────────┬─────────────────────────┘
                                                       │
        ┌──────────────────┬───────────────────────────┼───────────────────────────┬──────────────────┐
        ▼                  ▼                           ▼                           ▼                  ▼
 ┌──────────────┐   ┌──────────────┐           ┌──────────────┐           ┌──────────────┐   ┌──────────────┐
 │  BIOMETRIC   │   │  CRIMINAL    │           │     ANPR     │           │   MISSING    │   │   DEFENCE    │
 │ ATTENDANCE   │   │  TRACKING    │           │   VEHICLES   │           │  CHILDREN    │   │  TACTICAL    │
 └──────┬───────┘   └──────┬───────┘           └──────┬───────┘           └──────┬───────┘   └──────┬───────┘
        │                  │                           │                           │                  │
        └──────────────────┴───────────────────────────┼───────────────────────────┴──────────────────┘
                                                       │
                                        ┌──────────────┴──────────────┐
                                        │  SHARED REACTION & DATA MESH│
                                        │  - AppContext State Store   │
                                        │  - Live Webcam & CCTV Engine│
                                        │  - FastAPI AI Verification  │
                                        │  - Instant PDF Dossier Gen  │
                                        └─────────────────────────────┘
```

---

## 🚀 Key Modules & Security Domains

### 🎓 1. Biometric Attendance System
- **Use Case:** Schools, Govt Colleges, Universities, and Corporate Hubs.
- **Highlights:**
  - Automated facial recognition turnstile check-ins eliminating proxy attendance.
  - Sector Selector: School, College, University, Corporate Hub.
  - Live absentee telemetry, check-in logs, and downloadable PDF attendance reports.

### 🚨 2. Criminal Tracking & Watchlist Intercept System
- **Use Case:** High-risk suspect tracking, wanted criminal alerts & law enforcement watchlist intercepts.
- **Highlights:**
  - **250ms Real-Time AI Scanner Loop** using ResNet-34 128-D Euclidean Distance matching (Threshold: `0.58`).
  - **👥 Multi-Face Crowd Sweep:** Tracks multiple faces simultaneously with dynamic color-coded bounding boxes.
  - **🔒 Zero-Flicker Match Hysteresis (3000ms):** Prevents UI jitter during live scanning.
  - **🛑 30-Second Debounce Protection:** Prevents duplicate notification flooding.
  - **📄 Instant PDF Intercept Dossier:** Generates official security dossiers (`CHAKRAVYUH_CRIMINAL_INTERCEPT_DOSSIER_[ID].pdf`).

### 🚘 3. Automatic Number Plate Recognition (ANPR)
- **Use Case:** Traffic command, toll gates, stolen vehicle tracking & smart city challan management.
- **Highlights:**
  - Real-time license plate OCR scanning for vehicles up to 180 km/h.
  - Automatic flag system for stolen vehicles, expired permits, and fake number plates.

### 🚸 4. Missing Children Rescue Spotlight System
- **Use Case:** Public transit hubs, railway stations, airports, and city surveillance for child recovery.
- **Highlights:**
  - Dedicated child case registries (`Case MC-2026-***`).
  - Yellow bounding box on face detection, Green bounding box on biometric match.
  - Automated visual gradient flash, Web Audio urgency beep tone, and text-to-speech voice announcements.
  - Auto-generated detection match reports saved locally and accessible in Reports & Logs.

### 🛡️ 5. Defence Tactical & Perimeter Security System
- **Use Case:** Military garrisons, armory vaults, border RADAR, and counter-drone defense.
- **Highlights:**
  - Armory biometric authorization clearance levels.
  - Thermal RADAR perimeter breach detection & emergency Lockdown trigger.

---

## 🛠️ Tech Stack & Technologies

| Layer | Technology | Description |
| :--- | :--- | :--- |
| **Frontend UI** | React 18 + React Router v6 | High-performance reactive component framework |
| **Build System** | Vite 5 | Instant HMR and optimized production bundling |
| **Styling & Theme** | Vanilla CSS + TailwindCSS | Pure White Light UI, clean glassmorphism, responsive grids |
| **AI Biometric Engine** | `@vladmandic/face-api` | SSD MobileNet V1 + ResNet-34 128-D facial descriptor matching |
| **Backend Framework** | Python 3.10+ / FastAPI / Uvicorn | Async REST API for microservices & validation |
| **PDF Dossiers** | `jsPDF` | Real-time client-side generation of security dossier reports |
| **Geospatial Mapping** | `Leaflet` + `react-leaflet` | Live interactive surveillance map with camera nodes |
| **Data Visualization** | `Recharts` | Real-time security analytics and incident breakdown charts |
| **Icons** | `lucide-react` | Clean vector iconography |

---

## ⚙️ Installation & Local Setup

### 📋 Prerequisites
- **Node.js** v18.0.0 or higher
- **npm** v9.0.0 or higher
- **Python** 3.10+ *(Optional, for FastAPI server)*

---

### 💻 1. Frontend Setup (React + Vite)

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/Project-Chakravyuh.git

# Navigate into prototype folder
cd Project-Chakravyuh/Project-Chakravyuh-Prototype

# Install npm packages
npm install

# Run Vite dev server
npm run dev
```
Open **[http://localhost:5173](http://localhost:5173)** in your browser.

---

### 🐍 2. Backend Setup (FastAPI Python API)

```bash
# From Project-Chakravyuh-Prototype directory
# Install python dependencies
pip install -r backend/requirements.txt

# Start FastAPI Uvicorn Server
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```
API Root: **[http://127.0.0.1:8000](http://127.0.0.1:8000)**  
Swagger Docs: **[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)**

---

## 📁 Repository Structure

```text
Project-Chakravyuh/
└── Project-Chakravyuh-Prototype/
    ├── public/
    │   └── models/                      # Pretrained Face-API AI Models (ResNet-34, SSD, TinyFace)
    ├── backend/
    │   ├── main.py                      # FastAPI App Entry point & CORS setup
    │   ├── requirements.txt             # Python backend dependencies
    │   └── routers/                     # FastAPI route modules (auth, ai_engine, modules)
    ├── src/
    │   ├── components/                  # Reusable UI components (Topbar, Sidebar, CctvView, StatCard)
    │   ├── context/                     # AppContext global state store (Alerts, Watchlist, Reports)
    │   ├── data/                        # Core data mocks (Alerts, Personnel, Watchlist, Cameras)
    │   ├── layouts/                     # MainLayout wrapper component
    │   ├── pages/
    │   │   ├── PurposeSelector.jsx      # Multi-Domain Purpose Gateway Page
    │   │   ├── ModuleLogin.jsx          # Domain Sector Login Page
    │   │   ├── Dashboard.jsx            # Dynamic Command Dashboard
    │   │   ├── CriminalTracking.jsx     # Live AI Facial Recognition & Dossier Generator
    │   │   ├── Attendance.jsx           # Biometric Check-in Roster
    │   │   ├── MissingChild.jsx         # Missing Children Sonar Search Spotlight
    │   │   ├── ANPR.jsx                 # Automatic License Plate Scanning
    │   │   ├── TacticalDefense.jsx      # Military Perimeter Security Control
    │   │   ├── Alerts.jsx               # Security Alert Log & Triage Desk
    │   │   ├── Reports.jsx              # System PDF Audit & Match Report Center
    │   │   ├── Cameras.jsx              # CCTV Matrix & Stream Feeds
    │   │   └── Maps.jsx                 # Live Geospatial Surveillance Map
    │   ├── App.jsx                      # App Routes & Protected Layout
    │   ├── main.jsx                     # React DOM Entry point
    │   └── index.css                    # Master CSS styling rules
    ├── package.json                     # Node.js dependencies & scripts
    ├── vite.config.js                   # Vite configuration
    └── README.md                        # Documentation
```

---

## 🔌 API Endpoints (FastAPI Backend)

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/` | API Health Check & System Status |
| `POST` | `/api/auth/login` | Module Security Authentication |
| `POST` | `/api/ai/match-face` | Server-side Facial Embedding Verification |
| `GET` | `/api/modules/summary` | Real-time System Metrics Summary |

---

## 📄 License & Attribution

This project is built for defense, law enforcement, enterprise attendance, and smart city infrastructure under **Project Chakravyuh 2.0**. All AI models belong to open-source face-api / ResNet libraries.

---

<p align="center">
  <b>Made with ❤️ for Bharat 2.0 AI Security & Surveillance Infrastructure</b>
</p>

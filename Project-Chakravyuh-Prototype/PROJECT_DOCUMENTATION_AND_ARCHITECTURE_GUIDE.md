# 🛡️ PROJECT CHAKRAVYUH v2.0 — FULL SYSTEM ARCHITECTURE & DOCUMENTATION MANUAL

---

## 📌 Executive Summary
**Project Chakravyuh v2.0** is an **Enterprise Multi-Purpose AI Security, Biometric Surveillance & Tactical Intelligence Command Platform**. Built with React 18, Vite 5, TailwindCSS, `@vladmandic/face-api` (ResNet-34 128-D Biometric Embeddings), and a High-Performance FastAPI Python Backend.

---

## 🏛️ System Architecture Overview

```
                          ┌─────────────────────────────────────────────────┐
                          │         CHAKRAVYUH PURPOSE SELECTOR             │
                          │   (Multi-Domain Operational Security Gateway)   │
                          └───────────────────────┬─────────────────────────┘
                                                  │
       ┌──────────────────┬───────────────────────┼───────────────────────┬──────────────────┐
       ▼                  ▼                       ▼                       ▼                  ▼
┌──────────────┐   ┌──────────────┐       ┌──────────────┐       ┌──────────────┐   ┌──────────────┐
│  BIOMETRIC   │   │  CRIMINAL    │       │     ANPR     │       │   MISSING    │   │   DEFENCE    │
│ ATTENDANCE   │   │  TRACKING    │       │   VEHICLES   │       │  CHILDREN    │   │  TACTICAL    │
└──────┬───────┘   └──────┬───────┘       └──────┬───────┘       └──────┬───────┘   └──────┬───────┘
       │                  │                       │                       │                  │
       └──────────────────┴───────────────────────┼───────────────────────┴──────────────────┘
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

## 🚀 Key Modules & Operational Security Domains

### 1. 🎓 Biometric Attendance System
- **Purpose:** Contactless AI facial recognition check-in for Government Schools, Govt Colleges, State Universities, and Enterprise Hubs.
- **Key Features:**
  - Automated turnstile & campus entry check-ins eliminating proxy attendance.
  - Sector Selector: Govt School / Govt College / State University / Govt Enterprise.
  - Roster management, entry timestamps, absentee telemetry, and attendance PDF audit generation.

### 2. 🚨 Criminal Tracking & Watchlist Intercept System
- **Purpose:** Real-time suspect facial recognition against high-risk wanted criminal databases.
- **Key Features:**
  - **Ultra-Fast 250ms Real-Time Scanner Loop** with ResNet-34 128-D Euclidean Distance matching (`0.58` optimal match threshold).
  - **👥 Multi-Face Crowd Sweep Radar:** Detects and tracks 1, 2, 3 or more faces in frame simultaneously with distinct color-coded bounding box overlays.
  - **🔒 Zero-Flicker Match Hysteresis Hold (3000ms):** Holds match state solid without flickering.
  - **🛑 30-Second Target Alert Debounce:** Prevents notification spamming.
  - **📄 Instant PDF Intercept Dossier Generator:** Instant download of official government security Dossier reports (`CHAKRAVYUH_CRIMINAL_INTERCEPT_DOSSIER_[ID].pdf`).

### 3. 🚘 Automatic Number Plate Recognition (ANPR)
- **Purpose:** Real-time license plate OCR & vehicle intercept system.
- **Key Features:**
  - High-speed OCR plate scanning (tracks stolen vehicles, expired permits, fake plates, and speed violations up to 180 km/h).
  - Sector Selector: State Traffic Command, Expressway Toll, Stolen Vehicle Cell, Smart City Challan Hub.

### 4. 🚸 Missing Children Rescue Spotlight System
- **Purpose:** AI-driven facial search & sonar sweeps for locating missing children across public transit nodes.
- **Key Features:**
  - Specialized missing child case registries (`Case MC-2026-***`).
  - Strict notification isolation ensuring Missing Child alerts do not bleed into other security modules.
  - Hospital recovery desk & transit patrol notification dispatch.

### 5. 🛡️ Defence Tactical & Perimeter Security System
- **Purpose:** Military-grade command center for garrison bases, armory vaults, and border thermal RADAR.
- **Key Features:**
  - Armory vault biometric access clearance.
  - Thermal RADAR perimeter breach detection & counter-drone defense.
  - Sector Selector: Garrison Command Bunker, Airbase Security Guard, Border Thermal RADAR, Tactical QRT Mobile.

---

## 🛠️ Technology Stack

| Layer | Technology | Purpose |
| :--- | :--- | :--- |
| **Frontend UI** | React 18 (Hooks, Context, React Router v6) | Reactive, modular component architecture |
| **Build System** | Vite 5 | Fast HMR & production bundle optimization |
| **Styling** | Vanilla CSS + TailwindCSS | Pure white light mode UI, modern glassmorphism, responsive grids |
| **AI Biometric Engine** | `@vladmandic/face-api` (ResNet-34 + SSD MobileNet V1) | Local 128-D facial feature descriptor extraction & matching |
| **Backend AI API** | Python 3.10+ / FastAPI / Uvicorn | Server-side face verification & RESTful microservices |
| **PDF Reporting** | `jsPDF` | Client-side generation of official PDF Intercept Dossiers |
| **Icons & Visuals** | `lucide-react` | Clean, modern vector iconography |

---

## 💻 How to Run the Project Locally

### 1. Prerequisites
- **Node.js**: v18.0.0 or higher
- **Python**: v3.9+ (Optional for FastAPI backend)

### 2. Frontend Setup & Execution
```bash
# Navigate to project directory
cd Project-Chakravyuh-Prototype

# Install dependencies
npm install

# Start Vite Development Server
npm run dev
```
Open [http://localhost:5173](http://localhost:5173) in your browser.

### 3. Backend Setup (Optional Python FastAPI Server)
```bash
# Run FastAPI Backend with Uvicorn
py -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

---

## 📁 Project Directory Structure

```
Project-Chakravyuh-Prototype/
├── public/
│   └── models/                      # Pretrained Face-API AI Models (ResNet-34, SSD, TinyFace)
├── backend/
│   └── main.py                      # FastAPI Python Backend Server
├── src/
│   ├── components/                  # Reusable UI Components (Topbar, Sidebar, CctvView, StatCard)
│   ├── context/                     # AppContext global state store (Alerts, Watchlist, Personnel)
│   ├── data/                        # Initial mock data (Alerts, Personnel, Watchlist, Cameras)
│   ├── layouts/                     # MainLayout wrapper
│   ├── pages/
│   │   ├── PurposeSelector.jsx      # Purpose Selector Landing Page
│   │   ├── ModuleLogin.jsx          # Domain Sector Module Sign-In Page
│   │   ├── Dashboard.jsx            # Module Private Operational Dashboards
│   │   ├── CriminalTracking.jsx     # Live AI Facial Recognition & PDF Dossier Generator
│   │   ├── Attendance.jsx           # Biometric Attendance Roster & Check-ins
│   │   ├── Alerts.jsx               # Incident Alert Log & Triage
│   │   ├── Reports.jsx              # System PDF Audit Report Center
│   │   ├── Cameras.jsx              # Live CCTV Node Surveillance Grid
│   │   └── Maps.jsx                 # Geospatial Command Map
│   ├── App.jsx                      # React Router Configuration & Protected Routes
│   ├── main.jsx                     # Entry Point
│   └── index.css                    # Global CSS Styles & Smooth Scroll Rules
├── package.json                     # Frontend Dependencies
├── vite.config.js                   # Vite Build Configuration
└── PROJECT_DOCUMENTATION_AND_ARCHITECTURE_GUIDE.md
```

---
*© 2026 Project Chakravyuh — Smart Security & Surveillance Command System.*

<div align="center">

# 🛡️ PROJECT CHAKRAVYUH v2.0

### **Bharat 2.0 Enterprise AI Tactical Security, Biometric Surveillance & Intelligence Command Platform**

[![React](https://img.shields.io/badge/React-18.3.1-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://react.dev/)
[![Vite](https://img.shields.io/badge/Vite-5.4.14-646CFF?style=for-the-badge&logo=vite&logoColor=white)](https://vitejs.dev/)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-3.4.17-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white)](https://tailwindcss.com/)
[![AI Engine](https://img.shields.io/badge/AI_Engine-ResNet34_128D-FF6F00?style=for-the-badge&logo=tensorflow&logoColor=white)](https://github.com/vladmandic/face-api)

---

</div>

## 📌 Executive Overview

**Project Chakravyuh v2.0** is an **All-in-One Multi-Domain Tactical AI Command & Surveillance Gateway** engineered for smart cities, law enforcement, defense garrisons, and enterprise campuses. 

It provides **sub-millisecond biometric facial recognition**, **multi-target crowd scanning**, **automatic license plate recognition (ANPR)**, **missing children sonar sweeps**, and **defense thermal RADAR**—all accessible via a unified, modern White-Theme Command Portal.

---

## 🏛️ System Architecture & Data Flow

```text
                                ┌───────────────────────────────────────────────────┐
                                │         CHAKRAVYUH PURPOSE SELECTOR               │
                                │   (Multi-Domain Operational Security Gateway)     │
                                └────────────────────────┬──────────────────────────┘
                                                         │
        ┌───────────────────┬────────────────────────────┼────────────────────────────┬───────────────────┐
        ▼                   ▼                            ▼                            ▼                   ▼
 ┌───────────────┐   ┌───────────────┐           ┌───────────────┐           ┌───────────────┐   ┌───────────────┐
 │  BIOMETRIC    │   │   CRIMINAL    │           │     ANPR      │           │    MISSING    │   │    DEFENCE    │
 │  ATTENDANCE   │   │   TRACKING    │           │   VEHICLES    │           │   CHILDREN    │   │   TACTICAL    │
 └───────┬───────┘   └───────┬───────┘           └───────┬───────┘           └───────┬───────┘   └───────┬───────┘
         │                   │                           │                           │                   │
         └───────────────────┴───────────────────────────┼───────────────────────────┴───────────────────┘
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

## 🤖 Core AI & Computer Vision Stack

| Technology | Category | Role in Project Chakravyuh |
| :--- | :--- | :--- |
| **OpenCV** | Computer Vision Library (C++/Python) | Frame preprocessing, contour detection & canvas overlay rendering |
| **EasyOCR** | OCR Recognition Library (Python) | High-speed vehicle license plate character extraction (ANPR) |
| **Face-API / ResNet-34** | Biometric AI Neural Network | Live face detection, 128-D descriptor embedding extraction & Euclidean matching |
| **YOLOv8** | Object Detection AI Framework | Real-time crowd sweeping, person & threat object detection |

---

## ⚡ Key Highlights & Innovation Standard

- **⚡ 250ms Real-Time AI Scanner Loop:** Deep facial descriptor comparison running every 250ms using ResNet-34 128-D Euclidean Distance vectors.
- **👥 Multi-Face Crowd Sweep:** Detects, tracks, and bounds multiple faces in a single live webcam frame simultaneously with distinct color overlays.
- **🔒 Zero-Flicker Match Hysteresis Hold (3000ms):** UI locks on match targets solidly without bounding-box flickering.
- **📄 Instant PDF Intercept Dossier Generator:** One-click download of official law enforcement dossiers (`CHAKRAVYUH_CRIMINAL_INTERCEPT_DOSSIER_[ID].pdf`).
- **🚸 Automated Missing Child Radar & Detection Reports:** Screen flash effect, audio beep alarm, voice speech synthesis, and persistent detection logs.
- **🛡️ Sector-Based Security Controls:** Independent login gateways for School, University, Law Enforcement, Traffic Command, and Defense Garrison sectors.

---

## 🚀 Specialized Operational Modules

### 🎓 1. Biometric Attendance System
- **Domains:** Schools, Govt Colleges, State Universities, Enterprise Hubs.
- **Features:** Automated facial check-ins, proxy-proof turnstiles, real-time absentee counters, and PDF roster exports.

### 🚨 2. Criminal Tracking & Watchlist Intercept System
- **Domains:** High-risk suspect search, Wanted criminal alerts, Airport & Transit intercepts.
- **Features:** Multi-face crowd radar, 0.58 distance threshold match, 30-sec target alert debounce, and instant PDF Intercept Dossier creation.

### 🚘 3. Automatic Number Plate Recognition (ANPR)
- **Domains:** Highway toll plazas, Smart city traffic command, Stolen vehicle cell.
- **Features:** Optical Character Recognition (OCR) plate scanner (up to 180 km/h vehicle speed tracking), stolen vehicle flags, expired permit alerts.

### 🚸 4. Missing Children Rescue Spotlight System
- **Domains:** Railway stations, Bus terminals, Airports, Hospital recovery desks.
- **Features:** Case registry system (`Case MC-2026-***`), green match rectangle, audio-visual spotlight alert, and auto-generated rescue reports.

### 🛡️ 5. Defence Tactical & Perimeter Security System
- **Domains:** Army base garrisons, Armory vaults, Border thermal RADAR, QRT mobile units.
- **Features:** Biometric clearance verification, thermal perimeter breach radar, and base-wide Emergency Lockdown trigger.

---

## 🛠️ Complete Technology Stack

| Layer | Technology | Function |
| :--- | :--- | :--- |
| **Frontend UI** | **React 18** (Hooks + Context API) | Modular, reactive UI component architecture |
| **Build Tooling** | **Vite 5** | Lightning-fast HMR and optimized asset bundling |
| **Styling & Theme** | **TailwindCSS 3.4** + Vanilla CSS | Pure White Light theme, modern glassmorphism, responsive cards |
| **AI Biometric Engine**| `@vladmandic/face-api` | SSD MobileNet V1 + ResNet-34 128-D facial feature embeddings |
| **Backend API** | **Python 3.10+ / FastAPI / Uvicorn** | Server-side validation, microservices & async endpoints |
| **PDF Dossiers** | **jsPDF** | Client-side official PDF dossier generator |
| **Interactive Maps** | **Leaflet + React-Leaflet** | Live geospatial surveillance camera node tracking |
| **Analytics Charts** | **Recharts** | Real-time incident telemetry and visual breakdowns |
| **Icons** | **Lucide React** | Modern vector icon suite |

---

## ⚙️ Getting Started & Installation Guide

### 📋 Prerequisites
- **Node.js** v18.0.0 or higher
- **npm** v9.0.0 or higher
- **Python** 3.10+ *(Optional, for FastAPI server)*

---

### 💻 Step 1: Clone & Run Frontend (React + Vite)

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/Project-Chakravyuh.git

# Navigate to the prototype directory
cd Project-Chakravyuh/Project-Chakravyuh-Prototype

# Install dependencies
npm install

# Start Vite dev server
npm run dev
```


---

### 🐍 Step 2: Start FastAPI Python Backend Server (Optional)

```bash
# From Project-Chakravyuh-Prototype directory
pip install -r backend/requirements.txt

# Start backend server with uvicorn
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```
Live Link - https://6a9864ad425542223958a984--famous-lebkuchen-86e7d1.netlify.app/

---

## 📁 Repository Directory Structure

```text
Project-Chakravyuh/
└── Project-Chakravyuh-Prototype/
    ├── public/
    │   └── models/                      # Pretrained Face-API AI Models (ResNet-34, SSD, TinyFace)
    ├── backend/
    │   ├── main.py                      # FastAPI server entry point & CORS
    │   ├── requirements.txt             # Python backend dependencies
    │   └── routers/                     # Microservice routers (auth, ai_engine, modules)
    ├── src/
    │   ├── components/                  # Reusable UI (Topbar, Sidebar, CctvView, StatCard)
    │   ├── context/                     # AppContext global state store (Alerts, Watchlist, Reports)
    │   ├── data/                        # Initial mock data (Alerts, Personnel, Watchlist, Cameras)
    │   ├── layouts/                     # MainLayout layout wrapper
    │   ├── pages/
    │   │   ├── PurposeSelector.jsx      # Purpose Gateway Landing Page
    │   │   ├── ModuleLogin.jsx          # Sector Sign-In Gateway
    │   │   ├── Dashboard.jsx            # Dynamic Command Center Dashboard
    │   │   ├── CriminalTracking.jsx     # Live AI Facial Scanning & Dossier Generator
    │   │   ├── Attendance.jsx           # Biometric Attendance Roster
    │   │   ├── MissingChild.jsx         # Missing Children Sonar Radar
    │   │   ├── ANPR.jsx                 # Automatic License Plate Scanning
    │   │   ├── TacticalDefense.jsx      # Military Base Perimeter Security
    │   │   ├── Alerts.jsx               # Security Incident Alert Desk
    │   │   ├── Reports.jsx              # PDF Intercept & Audit Report Center
    │   │   ├── Cameras.jsx              # Live CCTV Node Grid
    │   │   └── Maps.jsx                 # Live Geospatial Map View
    │   ├── App.jsx                      # React Router Configuration & Protected Routes
    │   ├── main.jsx                     # Application Entry Point
    │   └── index.css                    # Global Styles & Custom Animations
    ├── package.json                     # Node.js dependencies
    ├── vite.config.js                   # Vite configuration
    └── README.md                        # Project Documentation
```

---

## 🔌 API Endpoints Reference

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/` | System Health Check & Version |
| `POST` | `/api/auth/login` | Sector Module Authentication |
| `POST` | `/api/ai/match-face` | Facial Embedding Vector Comparison |
| `GET` | `/api/modules/summary` | Real-time Incident & Metric Telemetry |

---

## 📜 License & Compliance

Developed under **Project Chakravyuh 2.0 Infrastructure**. Built for law enforcement, government institutions, and defense operations. AI facial recognition relies on open-source ResNet-34 neural networks.

---

<div align="center">

**Made with ❤️ for Bharat 2.0 AI Security & Tactical Intelligence Infrastructure**

</div>


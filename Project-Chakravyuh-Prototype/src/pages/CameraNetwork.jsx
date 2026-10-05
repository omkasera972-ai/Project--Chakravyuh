import React, { useState, useEffect } from 'react';
import {
  Video,
  Grid,
  List,
  Activity,
  ShieldCheck,
  AlertTriangle,
  Search,
  MapPin,
  Plus,
  Check,
  X,
  Trash2,
  Globe,
  Navigation
} from 'lucide-react';
import { MapContainer, TileLayer, Marker, Popup, useMap, useMapEvents } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { useApp } from '../context/AppContext';
import { StatCard } from '../components/StatCard';
import { CctvView } from '../components/CctvView';

// Fix Leaflet marker icon URLs
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.7.1/dist/images/marker-icon-2x.png',
  iconUrl: 'https://unpkg.com/leaflet@1.7.1/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.7.1/dist/images/marker-shadow.png',
});

// Map Controller Component for programmatically flying to search results
const MapFlyTo = ({ center }) => {
  const map = useMap();
  useEffect(() => {
    if (center && center[0] && center[1]) {
      map.flyTo(center, 15, { animate: true, duration: 1.5 });
    }
  }, [center, map]);
  return null;
};

// Location Marker Picker Component for click & drag map selection
const LocationMarkerPicker = ({ position, setPosition, setAddress }) => {
  useMapEvents({
    click(e) {
      const newPos = [e.latlng.lat, e.latlng.lng];
      setPosition(newPos);
      fetchAddress(e.latlng.lat, e.latlng.lng, setAddress);
    },
  });

  return position ? (
    <Marker
      position={position}
      draggable={true}
      eventHandlers={{
        dragend: (e) => {
          const marker = e.target;
          const pos = marker.getLatLng();
          const newPos = [pos.lat, pos.lng];
          setPosition(newPos);
          fetchAddress(pos.lat, pos.lng, setAddress);
        },
      }}
    />
  ) : null;
};

// Helper function for reverse geocoding
const fetchAddress = async (lat, lng, setAddress) => {
  try {
    const res = await fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lng}`);
    if (res.ok) {
      const data = await res.json();
      if (data && data.display_name) {
        setAddress(data.display_name);
      }
    }
  } catch (err) {
    console.warn('Reverse geocoding error:', err);
  }
};

export const CameraNetwork = () => {
  const { cameras = [], addCamera, deleteCamera, setSelectedCameraForModal, showToast } = useApp();
  const [viewMode, setViewMode] = useState('grid');
  const [filterStatus, setFilterStatus] = useState('All');
  const [searchTerm, setSearchTerm] = useState('');

  // Form State for Adding Camera
  const [camForm, setCamForm] = useState({
    id: `CAM-${Math.floor(1000 + Math.random() * 9000)}`,
    name: '',
    location: '',
    lat: 22.7196,
    lng: 75.8577
  });

  // Map Modal State
  const [isMapModalOpen, setIsMapModalOpen] = useState(false);
  const [mapSearchQuery, setMapSearchQuery] = useState('');
  const [tempPosition, setTempPosition] = useState([22.7196, 75.8577]); // Default Indore / MP coordinates
  const [tempAddress, setTempAddress] = useState('');
  const [isSearchingMap, setIsSearchingMap] = useState(false);

  // Handle Search in Map Modal (Nominatim Geocoding API)
  const handleMapSearch = async (e) => {
    if (e) e.preventDefault();
    if (!mapSearchQuery.trim()) return;

    setIsSearchingMap(true);
    try {
      const res = await fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(mapSearchQuery)}`);
      if (res.ok) {
        const data = await res.json();
        if (data && data.length > 0) {
          const firstResult = data[0];
          const newLat = parseFloat(firstResult.lat);
          const newLng = parseFloat(firstResult.lon);
          const newPos = [newLat, newLng];
          setTempPosition(newPos);
          setTempAddress(firstResult.display_name);
          if (showToast) showToast('Location Found', `Centered on ${firstResult.display_name.slice(0, 40)}...`, 'success');
        } else {
          if (showToast) showToast('Not Found', 'No map location found for search query.', 'error');
        }
      }
    } catch (err) {
      console.error('Map search error:', err);
    } finally {
      setIsSearchingMap(false);
    }
  };

  // Open Map Modal
  const openMapModal = () => {
    setTempPosition([camForm.lat || 22.7196, camForm.lng || 75.8577]);
    setTempAddress(camForm.location || '');
    setIsMapModalOpen(true);
  };

  // Confirm Location from Map
  const handleConfirmLocation = () => {
    setCamForm(prev => ({
      ...prev,
      lat: tempPosition[0],
      lng: tempPosition[1],
      location: tempAddress || prev.location || `Lat: ${tempPosition[0].toFixed(5)}, Lng: ${tempPosition[1].toFixed(5)}`
    }));
    setIsMapModalOpen(false);
    if (showToast) showToast('Location Selected', 'Coordinates & address loaded into camera form.', 'success');
  };

  // Save Camera Form Submit
  const handleSaveCamera = (e) => {
    e.preventDefault();
    if (!camForm.name.trim()) {
      if (showToast) showToast('Missing Name', 'Please enter Camera Name.', 'error');
      return;
    }
    if (!camForm.location.trim()) {
      if (showToast) showToast('Missing Location', 'Please select or enter Camera Location/Address.', 'error');
      return;
    }

    addCamera({
      id: camForm.id,
      name: camForm.name.trim(),
      address: camForm.location.trim(),
      location: camForm.location.trim(),
      lat: camForm.lat,
      lng: camForm.lng,
      status: 'Online',
      type: '4K Security Camera'
    });

    // Reset Form
    setCamForm({
      id: `CAM-${Math.floor(1000 + Math.random() * 9000)}`,
      name: '',
      location: '',
      lat: 22.7196,
      lng: 75.8577
    });
  };

  const totalCameras = cameras.length;
  const onlineCameras = cameras.filter(c => c.status === 'Online' || c.status === 'ACTIVE').length;
  const offlineCameras = cameras.filter(c => c.status === 'Offline').length;

  const filteredCameras = cameras.filter(c => {
    const matchesStatus = filterStatus === 'All' || c.status === filterStatus;
    const q = searchTerm.toLowerCase();
    const matchesSearch = (c.name || '').toLowerCase().includes(q) ||
                          (c.code || '').toLowerCase().includes(q) ||
                          (c.location || '').toLowerCase().includes(q) ||
                          (c.address || '').toLowerCase().includes(q) ||
                          (c.id || '').toLowerCase().includes(q);
    return matchesStatus && matchesSearch;
  });

  return (
    <div className="space-y-6 select-none pb-6">
      {/* Page Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-white dark:bg-[#11141c] border border-gray-200 dark:border-gray-800 p-6 rounded-2xl shadow-xs">
        <div>
          <h1 className="text-xl sm:text-2xl font-normal text-slate-800 dark:text-white tracking-normal">
            Camera Network Management
          </h1>
          <p className="text-xs sm:text-sm text-slate-500 dark:text-gray-400 mt-1 font-normal">
            Configure live CCTV network nodes, interactive GPS map locations, and streaming feeds.
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <div className="flex items-center bg-gray-100 dark:bg-[#171922] p-1 rounded-xl border border-gray-200 dark:border-gray-800">
            <button
              onClick={() => setViewMode('grid')}
              className={`p-2 rounded-lg text-xs font-normal transition-all cursor-pointer ${
                viewMode === 'grid' ? 'bg-white dark:bg-[#222631] text-blue-600 dark:text-white shadow-xs' : 'text-slate-500 hover:text-slate-800'
              }`}
            >
              <Grid className="w-4 h-4" />
            </button>
            <button
              onClick={() => setViewMode('table')}
              className={`p-2 rounded-lg text-xs font-normal transition-all cursor-pointer ${
                viewMode === 'table' ? 'bg-white dark:bg-[#222631] text-blue-600 dark:text-white shadow-xs' : 'text-slate-500 hover:text-slate-800'
              }`}
            >
              <List className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>

      {/* KPI Stats */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <StatCard title="Total Connected Nodes" value={String(totalCameras)} subtext="Active Network Nodes" icon={Video} />
        <StatCard title="Online Streams" value={String(onlineCameras)} subtext="Streaming Live" icon={ShieldCheck} />
        <StatCard title="Offline Nodes" value={String(offlineCameras)} subtext="Maintenance Needed" icon={AlertTriangle} />
        <StatCard title="Average Latency" value="18 ms" subtext="RTSP Low Latency" icon={Activity} />
      </div>

      {/* 🌟 CENTER CARD: ADD CAMERA NETWORK FORM */}
      <div className="w-full bg-white dark:bg-[#161922] p-6 sm:p-9 rounded-3xl border border-blue-100 dark:border-gray-800 shadow-md space-y-6 relative overflow-hidden">
        <div className="flex items-center space-x-4 pb-5 border-b border-gray-100 dark:border-gray-800">
          <div className="w-12 h-12 rounded-2xl bg-blue-50/80 text-blue-600 dark:text-blue-400 flex items-center justify-center font-normal text-2xl shadow-xs">
            📹
          </div>
          <div>
            <h2 className="text-xl sm:text-2xl font-normal text-slate-800 dark:text-white tracking-normal">
              Add Camera Network
            </h2>
            <p className="text-xs sm:text-sm text-slate-400 dark:text-gray-400 font-normal">
              Register a new live CCTV node with interactive GPS map coordinates.
            </p>
          </div>
        </div>

        <form onSubmit={handleSaveCamera} className="space-y-6 w-full">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
            {/* Field 1: Camera ID */}
            <div className="space-y-2">
              <label className="block text-slate-700 dark:text-gray-300 font-normal text-sm sm:text-base">
                Camera ID
              </label>
              <input
                type="text"
                value={camForm.id}
                onChange={(e) => setCamForm({ ...camForm, id: e.target.value })}
                placeholder="e.g. CAM-1001"
                required
                className="w-full h-[52px] px-4 bg-gray-50 dark:bg-slate-900/80 border border-gray-300 dark:border-gray-700 rounded-2xl text-slate-800 dark:text-white font-mono text-sm focus:outline-none focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10 transition-all"
              />
            </div>

            {/* Field 2: Camera Name */}
            <div className="space-y-2">
              <label className="block text-slate-700 dark:text-gray-300 font-normal text-sm sm:text-base">
                Camera Name
              </label>
              <input
                type="text"
                value={camForm.name}
                onChange={(e) => setCamForm({ ...camForm, name: e.target.value })}
                placeholder="e.g. Nemawar Chouraha CCTV Camera 1"
                required
                className="w-full h-[52px] px-4 bg-gray-50 dark:bg-slate-900/80 border border-gray-300 dark:border-gray-700 rounded-2xl text-slate-800 dark:text-white text-sm font-normal placeholder:text-slate-400 focus:outline-none focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10 transition-all"
              />
            </div>

            {/* Field 3: Camera Location / Address + Map Select Button */}
            <div className="space-y-2">
              <label className="block text-slate-700 dark:text-gray-300 font-normal text-sm sm:text-base flex items-center justify-between">
                <span>Camera Location / Address</span>
              </label>
              <div className="flex gap-2">
                <input
                  type="text"
                  value={camForm.location}
                  onChange={(e) => setCamForm({ ...camForm, location: e.target.value })}
                  placeholder="e.g. Nemawar Bypass Gate, MP"
                  required
                  className="w-full h-[52px] px-4 bg-gray-50 dark:bg-slate-900/80 border border-gray-300 dark:border-gray-700 rounded-2xl text-slate-800 dark:text-white text-sm font-normal placeholder:text-slate-400 focus:outline-none focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10 transition-all"
                />
                <button
                  type="button"
                  onClick={openMapModal}
                  className="px-4 h-[52px] rounded-2xl bg-blue-50 hover:bg-blue-100 text-blue-600 border border-blue-200 text-xs sm:text-sm font-normal flex items-center gap-1.5 shrink-0 transition-all cursor-pointer active:scale-95"
                >
                  <MapPin className="w-4 h-4 text-blue-600" />
                  <span>📍 Select Location on Map</span>
                </button>
              </div>
            </div>
          </div>

          {/* Lat Lng Readout Display */}
          {(camForm.lat || camForm.lng) && (
            <div className="flex items-center gap-4 text-xs font-mono text-slate-500 dark:text-gray-400 pt-1">
              <span className="px-3 py-1 rounded-xl bg-gray-100 dark:bg-slate-800 border border-gray-200 dark:border-gray-700">
                Latitude: <strong className="text-blue-600 dark:text-blue-400 font-normal">{Number(camForm.lat).toFixed(5)}</strong>
              </span>
              <span className="px-3 py-1 rounded-xl bg-gray-100 dark:bg-slate-800 border border-gray-200 dark:border-gray-700">
                Longitude: <strong className="text-blue-600 dark:text-blue-400 font-normal">{Number(camForm.lng).toFixed(5)}</strong>
              </span>
            </div>
          )}

          <div className="pt-2">
            <button
              type="submit"
              className="w-full h-[54px] rounded-2xl bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white font-medium text-base sm:text-lg shadow-lg shadow-blue-600/20 transition-all flex items-center justify-center space-x-2 cursor-pointer active:scale-[0.99]"
            >
              <Plus className="w-5 h-5" />
              <span>Save Camera</span>
            </button>
          </div>
        </form>
      </div>

      {/* Filter Tabs & Search Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div className="flex items-center space-x-2">
          {['All', 'Online', 'Offline'].map(status => (
            <button
              key={status}
              onClick={() => setFilterStatus(status)}
              className={`px-4 py-2 rounded-xl text-xs sm:text-sm font-normal transition-all cursor-pointer ${
                filterStatus === status
                  ? 'bg-blue-600 text-white shadow-xs'
                  : 'bg-white dark:bg-[#14161d] text-slate-600 dark:text-gray-400 border border-gray-200 dark:border-gray-800 hover:text-slate-900'
              }`}
            >
              {status} Cameras ({status === 'All' ? totalCameras : status === 'Online' ? onlineCameras : offlineCameras})
            </button>
          ))}
        </div>

        <div className="relative">
          <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Search camera name or ID..."
            className="pl-9 pr-4 py-2 bg-white dark:bg-[#14161d] border border-gray-200 dark:border-gray-800 rounded-xl text-xs sm:text-sm text-slate-800 dark:text-white placeholder-gray-400 focus:outline-none focus:border-blue-500"
          />
        </div>
      </div>

      {/* Grid View of Registered Cameras */}
      {viewMode === 'grid' ? (
        filteredCameras.length === 0 ? (
          <div className="p-12 text-center text-gray-500 dark:text-gray-400 text-sm bg-white dark:bg-[#121419] rounded-3xl border border-dashed border-gray-300 dark:border-gray-800 space-y-3">
            <Video className="w-10 h-10 text-gray-400 mx-auto opacity-60" />
            <p className="font-medium text-slate-700 dark:text-gray-300 text-base">No Registered Cameras Found</p>
            <p className="text-xs text-gray-400">Use the form above to add a camera node to the system.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
            {filteredCameras.map((cam) => (
              <div
                key={cam.id}
                className="bg-white dark:bg-[#121419] border border-gray-200 dark:border-gray-800 rounded-3xl p-5 space-y-4 shadow-sm hover:border-blue-500 transition-all group flex flex-col justify-between"
              >
                <div>
                  <CctvView
                    cameraCode={cam.id}
                    location={cam.name}
                    isLive={cam.status === 'Online'}
                    aspectRatio="aspect-[16/10]"
                    onClick={() => setSelectedCameraForModal(cam)}
                  />
                  <div className="mt-4 space-y-1">
                    <div className="flex items-center justify-between">
                      <h3 className="font-medium text-slate-800 dark:text-white text-base leading-tight">
                        {cam.name}
                      </h3>
                      <span className="px-2.5 py-0.5 rounded-full text-[10px] font-normal bg-emerald-50 text-emerald-600 border border-emerald-200">
                        {cam.status || 'Online'}
                      </span>
                    </div>
                    <p className="text-xs text-slate-500 dark:text-gray-400 font-normal">
                      📍 {cam.location || cam.address || cam.zone}
                    </p>
                    {cam.lat && cam.lng && (
                      <p className="text-[11px] font-mono text-blue-600 dark:text-blue-400">
                        Lat: {Number(cam.lat).toFixed(4)}, Lng: {Number(cam.lng).toFixed(4)}
                      </p>
                    )}
                  </div>
                </div>

                <div className="pt-3 border-t border-gray-100 dark:border-gray-800 flex items-center justify-between">
                  <button
                    onClick={() => setSelectedCameraForModal(cam)}
                    className="px-3 py-1.5 bg-blue-50 dark:bg-blue-950/60 text-blue-600 dark:text-blue-400 rounded-xl font-normal text-xs hover:bg-blue-100 transition-colors cursor-pointer"
                  >
                    Inspect Live Feed
                  </button>

                  <button
                    onClick={() => deleteCamera(cam.id)}
                    title="Remove Camera"
                    className="p-2 rounded-xl text-gray-400 hover:text-rose-600 hover:bg-rose-50 transition-colors cursor-pointer"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )
      ) : (
        /* Table View */
        <div className="bg-white dark:bg-[#121419] border border-gray-200 dark:border-gray-800 rounded-2xl p-4 shadow-sm">
          <div className="overflow-x-auto rounded-xl border border-gray-200 dark:border-gray-800">
            <table className="w-full text-left text-xs border-collapse">
              <thead>
                <tr className="bg-gray-50 dark:bg-[#171922] border-b border-gray-200 dark:border-gray-800 text-gray-500 dark:text-gray-400 font-normal uppercase tracking-wider text-[11px]">
                  <th className="py-3 px-4">Camera ID</th>
                  <th className="py-3 px-4">Camera Name</th>
                  <th className="py-3 px-4">Location / Address</th>
                  <th className="py-3 px-4">GPS Coordinates</th>
                  <th className="py-3 px-4">Status</th>
                  <th className="py-3 px-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100 dark:divide-gray-800">
                {filteredCameras.map((cam) => (
                  <tr key={cam.id} className="hover:bg-gray-50 dark:hover:bg-[#161820] transition-colors">
                    <td className="py-3 px-4 font-mono font-normal text-slate-800 dark:text-white">{cam.id}</td>
                    <td className="py-3 px-4 font-normal text-slate-800 dark:text-white">{cam.name}</td>
                    <td className="py-3 px-4 text-slate-600 dark:text-gray-300">{cam.location || cam.address}</td>
                    <td className="py-3 px-4 font-mono text-blue-600 dark:text-blue-400">
                      {cam.lat && cam.lng ? `${Number(cam.lat).toFixed(4)}, ${Number(cam.lng).toFixed(4)}` : '--'}
                    </td>
                    <td className="py-3 px-4">
                      <span className="px-2.5 py-0.5 rounded-full text-[10px] font-normal bg-emerald-50 text-emerald-600 border border-emerald-200">
                        {cam.status || 'Online'}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-right space-x-2">
                      <button
                        onClick={() => setSelectedCameraForModal(cam)}
                        className="px-3 py-1 rounded-xl bg-blue-50 text-blue-600 font-normal text-xs"
                      >
                        Inspect
                      </button>
                      <button
                        onClick={() => deleteCamera(cam.id)}
                        className="px-3 py-1 rounded-xl bg-rose-50 text-rose-600 font-normal text-xs"
                      >
                        Delete
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* 🌟 LIVE INTERACTIVE MAP SELECTION MODAL */}
      {isMapModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm animate-fadeIn select-none">
          <div className="bg-white dark:bg-[#14161f] w-full max-w-4xl rounded-3xl shadow-2xl border border-gray-200 dark:border-gray-800 overflow-hidden flex flex-col max-h-[90vh]">
            
            {/* Modal Header */}
            <div className="p-5 border-b border-gray-200 dark:border-gray-800 flex items-center justify-between bg-gray-50 dark:bg-[#181a25]">
              <div className="flex items-center space-x-3">
                <div className="p-2 rounded-xl bg-blue-50 text-blue-600">
                  <Globe className="w-6 h-6" />
                </div>
                <div>
                  <h3 className="text-lg font-normal text-slate-800 dark:text-white">
                    🗺️ Live Location Map Selection
                  </h3>
                  <p className="text-xs text-slate-400 dark:text-gray-400">
                    Search location, zoom/pan, click anywhere to place marker or drag marker to set exact camera coordinates.
                  </p>
                </div>
              </div>
              <button
                onClick={() => setIsMapModalOpen(false)}
                className="p-2 rounded-xl hover:bg-gray-200 dark:hover:bg-gray-800 text-gray-500 transition-colors cursor-pointer"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Map Search Bar */}
            <div className="p-4 bg-white dark:bg-[#14161f] border-b border-gray-100 dark:border-gray-800 flex gap-2">
              <div className="relative flex-1">
                <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
                <input
                  type="text"
                  value={mapSearchQuery}
                  onChange={(e) => setMapSearchQuery(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && handleMapSearch(e)}
                  placeholder="🔍 Search location name, city, landmark, chouraha..."
                  className="w-full pl-9 pr-4 py-2.5 bg-gray-50 dark:bg-slate-900 border border-gray-300 dark:border-gray-700 rounded-xl text-xs sm:text-sm text-slate-800 dark:text-white placeholder-gray-400 focus:outline-none focus:border-blue-500"
                />
              </div>
              <button
                onClick={handleMapSearch}
                disabled={isSearchingMap}
                className="px-5 py-2.5 bg-blue-600 hover:bg-blue-700 text-white rounded-xl text-xs sm:text-sm font-normal flex items-center gap-1.5 transition-all cursor-pointer shrink-0"
              >
                <Navigation className="w-4 h-4" />
                <span>{isSearchingMap ? 'Searching...' : 'Search Location'}</span>
              </button>
            </div>

            {/* Leaflet Live Map View Container */}
            <div className="relative w-full h-[400px] bg-slate-900 overflow-hidden">
              <MapContainer
                center={tempPosition}
                zoom={14}
                style={{ width: '100%', height: '100%' }}
                className="z-10"
              >
                <TileLayer
                  attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                  url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                />
                <MapFlyTo center={tempPosition} />
                <LocationMarkerPicker
                  position={tempPosition}
                  setPosition={setTempPosition}
                  setAddress={setTempAddress}
                />
              </MapContainer>

              {/* Instruction Badge Overlay */}
              <div className="absolute top-3 left-3 z-20 px-3 py-1.5 rounded-xl bg-white/90 dark:bg-slate-900/90 backdrop-blur-md text-slate-700 dark:text-gray-200 text-xs font-normal shadow-md border border-gray-200 dark:border-gray-700 flex items-center gap-2">
                <MapPin className="w-4 h-4 text-blue-600" />
                <span>Click anywhere on map or drag marker to set exact location pin</span>
              </div>
            </div>

            {/* Coordinates & Reverse-Geocoded Address Display */}
            <div className="p-4 bg-gray-50 dark:bg-[#181a25] border-t border-gray-200 dark:border-gray-800 space-y-2">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 text-xs font-mono">
                <div className="flex items-center space-x-3">
                  <span className="px-3 py-1 rounded-lg bg-blue-100 text-blue-700 font-normal">
                    Latitude: <strong>{tempPosition[0].toFixed(5)}</strong>
                  </span>
                  <span className="px-3 py-1 rounded-lg bg-blue-100 text-blue-700 font-normal">
                    Longitude: <strong>{tempPosition[1].toFixed(5)}</strong>
                  </span>
                </div>
              </div>

              {tempAddress && (
                <div className="p-2.5 rounded-xl bg-white dark:bg-slate-900 border border-gray-200 dark:border-gray-800 text-xs text-slate-700 dark:text-gray-300 truncate">
                  📍 <strong>Auto Address:</strong> {tempAddress}
                </div>
              )}
            </div>

            {/* Modal Footer Controls */}
            <div className="p-4 bg-white dark:bg-[#14161f] border-t border-gray-200 dark:border-gray-800 flex items-center justify-end space-x-3">
              <button
                onClick={() => setIsMapModalOpen(false)}
                className="px-5 py-2.5 rounded-xl text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800 text-xs sm:text-sm font-normal cursor-pointer"
              >
                Cancel
              </button>
              <button
                onClick={handleConfirmLocation}
                className="px-6 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-700 text-white text-xs sm:text-sm font-normal shadow-md shadow-blue-600/20 transition-all flex items-center space-x-2 cursor-pointer"
              >
                <Check className="w-4 h-4" />
                <span>Confirm Location</span>
              </button>
            </div>

          </div>
        </div>
      )}
    </div>
  );
};

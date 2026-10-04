import React, { useState } from 'react';
import { X, UserPlus, Upload, Shield, Image as ImageIcon, PlusCircle, CheckCircle2 } from 'lucide-react';
import { useApp } from '../../context/AppContext';

export const AddPersonModal = () => {
  const { activeModal, setActiveModal, addPerson, personnel = [], showToast } = useApp();
  const [formData, setFormData] = useState({
    id: '',
    name: '',
    department: 'General Branch / Department',
    role: 'Student',
    camera: 'CAM-01',
    status: 'Registered',
    avatar: '👨‍🎓',
    photoUrl: ''
  });

  const [imagePreview, setImagePreview] = useState(null);
  const [photoError, setPhotoError] = useState(null);

  if (activeModal !== 'addPerson') return null;

  const memberTypes = [
    'Student',
    'Faculty / Teacher',
    'Dean / HOD / Management',
    'Staff Member / Officer',
    'Visitor / Guest'
  ];
  const avatars = ['👨‍🎓', '👩‍🎓', '👨‍🏫', '👩‍🏫', '👨‍💼', '👩‍💼', '🏛️', '👮‍♂️'];

  const handleFileChange = (e) => {
    const file = e.target.files && e.target.files[0];
    if (file) {
      setPhotoError(null);
      const reader = new FileReader();
      reader.onload = (event) => {
        const rawDataUrl = event.target.result;
        if (rawDataUrl) {
          setImagePreview(rawDataUrl);
          setFormData((prev) => ({ ...prev, photoUrl: rawDataUrl }));
          setPhotoError(null);

          const img = new Image();
          img.onload = () => {
            try {
              const canvas = document.createElement('canvas');
              const MAX_SIZE = 400;
              let width = img.width;
              let height = img.height;
              if (width > height) {
                if (width > MAX_SIZE) {
                  height *= MAX_SIZE / width;
                  width = MAX_SIZE;
                }
              } else {
                if (height > MAX_SIZE) {
                  width *= MAX_SIZE / height;
                  height = MAX_SIZE;
                }
              }
              canvas.width = width;
              canvas.height = height;
              const ctx = canvas.getContext('2d');
              ctx.drawImage(img, 0, 0, width, height);
              const compressedDataUrl = canvas.toDataURL('image/jpeg', 0.85);
              setImagePreview(compressedDataUrl);
              setFormData((prev) => ({ ...prev, photoUrl: compressedDataUrl }));
            } catch (err) {}
          };
          img.src = rawDataUrl;
        }
      };
      reader.readAsDataURL(file);
    }
  };

  const handleUrlChange = (e) => {
    const val = e.target.value;
    setPhotoError(null);
    setFormData((prev) => ({ ...prev, photoUrl: val }));
    setImagePreview(val || null);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setPhotoError(null);

    if (!formData.name.trim()) {
      if (showToast) showToast('Name Required', 'Please enter member full name.', 'warning');
      return;
    }

    const finalPhotoUrl = formData.photoUrl || imagePreview;
    if (!finalPhotoUrl || !String(finalPhotoUrl).trim()) {
      const errMsg = 'Member photo image is MANDATORY for AI face recognition attendance. Please upload a photo image.';
      setPhotoError(errMsg);
      if (showToast) {
        showToast('Photo Required ⚠️', errMsg, 'warning');
      }
      return;
    }

    let category = 'students';
    let prefix = 'STU';
    let baseNumber = 101;

    if (formData.role.includes('Faculty') || formData.role.includes('Teacher')) {
      category = 'faculties';
      prefix = 'TCH';
      baseNumber = 201;
    } else if (formData.role.includes('Dean') || formData.role.includes('HOD') || formData.role.includes('Management')) {
      category = 'leadership';
      prefix = 'ADM';
      baseNumber = 301;
    } else if (formData.role.includes('Staff') || formData.role.includes('Officer')) {
      category = 'leadership';
      prefix = 'EMP';
      baseNumber = 401;
    }

    let realId = formData.id.trim();
    if (!realId) {
      const categoryMembers = (personnel || []).filter(p => p && p.id && String(p.id).startsWith(prefix));
      const nextNum = baseNumber + categoryMembers.length;
      realId = `${prefix}-2026-${String(nextNum).padStart(3, '0')}`;
    }

    const res = await addPerson({
      ...formData,
      photoUrl: String(finalPhotoUrl).trim(),
      module: activeModule || 'attendance',
      category,
      designation: formData.role,
      id: realId,
      badgeId: `BADGE-${realId}`
    });

    if (res && res.success) {
      setActiveModal(null);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-md animate-in fade-in duration-200">
      <div className="bg-white dark:bg-[#12141c] border border-gray-200 dark:border-gray-800 rounded-3xl w-full max-w-xl overflow-hidden shadow-2xl transition-all">
        
        {/* Sleek Light Header Bar */}
        <div className="px-6 py-5 border-b border-gray-100 dark:border-gray-800 flex items-center justify-between bg-slate-50/80 dark:bg-[#0e1017]">
          <div className="flex items-center space-x-3.5">
            <div className="w-11 h-11 rounded-2xl bg-emerald-100 dark:bg-emerald-950/80 border border-emerald-300 dark:border-emerald-700 flex items-center justify-center text-emerald-600 dark:text-emerald-400 shadow-xs">
              <PlusCircle className="w-6 h-6 stroke-[2]" />
            </div>
            <div>
              <h3 className="text-gray-900 dark:text-white text-base sm:text-lg font-extrabold tracking-tight">
                Add New Data (Students, Teachers, Staff)
              </h3>
              <p className="text-gray-500 dark:text-gray-400 text-xs sm:text-sm font-medium mt-0.5">
                Enroll member details & photo image for biometric attendance check-in
              </p>
            </div>
          </div>
          <button
            onClick={() => setActiveModal(null)}
            className="p-2 rounded-xl text-gray-400 hover:text-gray-700 dark:hover:text-white hover:bg-gray-200/60 dark:hover:bg-gray-800 transition-colors cursor-pointer"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Form Body with Readable Bigger Fonts */}
        <form onSubmit={handleSubmit} className="p-6 sm:p-7 space-y-5 text-sm">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-gray-800 dark:text-gray-200 font-extrabold text-sm mb-1.5">
                Member Category / Role *
              </label>
              <select
                value={formData.role}
                onChange={(e) => setFormData({ ...formData, role: e.target.value })}
                className="w-full px-4 py-3 bg-gray-50 dark:bg-[#161922] border border-gray-200 dark:border-gray-800 rounded-2xl text-gray-900 dark:text-white font-bold focus:outline-none focus:border-emerald-500 focus:bg-white dark:focus:bg-[#1a1d27] text-sm"
              >
                {memberTypes.map(m => (
                  <option key={m} value={m}>{m}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-gray-800 dark:text-gray-200 font-extrabold text-sm mb-1.5">
                ID / Roll No / Staff Code
              </label>
              <input
                type="text"
                value={formData.id}
                onChange={(e) => setFormData({ ...formData, id: e.target.value })}
                placeholder="e.g. STU-2026-101 (Auto if blank)"
                className="w-full px-4 py-3 bg-gray-50 dark:bg-[#161922] border border-gray-200 dark:border-gray-800 rounded-2xl text-gray-900 dark:text-white placeholder-gray-400 font-mono font-bold focus:outline-none focus:border-emerald-500 focus:bg-white dark:focus:bg-[#1a1d27] text-sm"
              />
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-gray-800 dark:text-gray-200 font-extrabold text-sm mb-1.5">
                Full Name *
              </label>
              <input
                type="text"
                required
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                placeholder="e.g. Ananya Sharma"
                className="w-full px-4 py-3 bg-gray-50 dark:bg-[#161922] border border-gray-200 dark:border-gray-800 rounded-2xl text-gray-900 dark:text-white font-semibold placeholder-gray-400 focus:outline-none focus:border-emerald-500 focus:bg-white dark:focus:bg-[#1a1d27] text-sm"
              />
            </div>

            <div>
              <label className="block text-gray-800 dark:text-gray-200 font-extrabold text-sm mb-1.5">
                Department / Class / Branch
              </label>
              <input
                type="text"
                value={formData.department}
                onChange={(e) => setFormData({ ...formData, department: e.target.value })}
                placeholder="e.g. Computer Science / Class 10-A"
                className="w-full px-4 py-3 bg-gray-50 dark:bg-[#161922] border border-gray-200 dark:border-gray-800 rounded-2xl text-gray-900 dark:text-white font-semibold placeholder-gray-400 focus:outline-none focus:border-emerald-500 focus:bg-white dark:focus:bg-[#1a1d27] text-sm"
              />
            </div>
          </div>

          {/* Photo Image Upload Section */}
          <div className="space-y-2">
            <label className="block text-gray-800 dark:text-gray-200 font-extrabold text-sm flex items-center justify-between">
              <span>
                Upload Member Photo Image <span className="text-rose-500 font-bold">* (Mandatory for AI Scanner)</span>
              </span>
              {photoError && <span className="text-xs text-rose-500 font-black animate-pulse">Photo Required!</span>}
            </label>
            <div className={`flex items-center gap-4 p-4 rounded-2xl transition-all border ${
              photoError ? 'border-rose-500 bg-rose-50/40 dark:bg-rose-950/20 ring-2 ring-rose-500/30' : 'bg-gray-50 dark:bg-[#161922] border-gray-200 dark:border-gray-800'
            }`}>
              <div className="w-16 h-16 rounded-2xl bg-white dark:bg-[#101217] border border-gray-300 dark:border-gray-700 overflow-hidden flex items-center justify-center text-3xl shadow-xs flex-shrink-0">
                {imagePreview || formData.photoUrl ? (
                  <img src={imagePreview || formData.photoUrl} alt="Member Preview" className="w-full h-full object-cover" />
                ) : (
                  <span className="text-slate-400">📷</span>
                )}
              </div>
              <div className="flex-1 space-y-2">
                <input
                  type="file"
                  accept="image/*"
                  onChange={handleFileChange}
                  className="block w-full text-xs text-gray-600 dark:text-gray-300 file:mr-3 file:py-2 file:px-4 file:rounded-xl file:border-0 file:text-xs file:font-bold file:bg-emerald-600 file:text-white hover:file:bg-emerald-500 cursor-pointer"
                />
                <input
                  type="url"
                  value={formData.photoUrl}
                  onChange={handleUrlChange}
                  placeholder="Or paste Photo URL link..."
                  className="w-full px-3.5 py-2 bg-white dark:bg-[#101217] border border-gray-200 dark:border-gray-800 rounded-xl text-gray-900 dark:text-white placeholder-gray-400 text-xs focus:outline-none focus:border-emerald-500 font-medium"
                />
              </div>
            </div>
            {photoError && (
              <p className="text-xs font-bold text-rose-600 dark:text-rose-400 bg-rose-100/90 dark:bg-rose-950/40 p-2.5 rounded-xl border border-rose-200 dark:border-rose-900 flex items-center gap-1.5 animate-in fade-in">
                <span>⚠️ {photoError}</span>
              </p>
            )}
          </div>

          <div>
            <label className="block text-gray-800 dark:text-gray-200 font-extrabold text-sm mb-2">
              Select Avatar Icon Fallback
            </label>
            <div className="flex items-center space-x-2.5 overflow-x-auto pb-1">
              {avatars.map((av) => (
                <button
                  type="button"
                  key={av}
                  onClick={() => setFormData({ ...formData, avatar: av })}
                  className={`w-10 h-10 rounded-2xl border text-xl flex items-center justify-center transition-all cursor-pointer ${
                    formData.avatar === av
                      ? 'bg-emerald-100 dark:bg-emerald-950/80 border-emerald-500 text-white shadow-sm ring-2 ring-emerald-500/30'
                      : 'bg-white dark:bg-[#15171e] border-gray-200 dark:border-gray-800 hover:border-gray-400'
                  }`}
                >
                  {av}
                </button>
              ))}
            </div>
          </div>

          <div className="flex items-center justify-end space-x-3 pt-5 border-t border-gray-100 dark:border-gray-800">
            <button
              type="button"
              onClick={() => setActiveModal(null)}
              className="px-5 py-3 rounded-2xl bg-gray-100 dark:bg-[#191b22] border border-gray-200 dark:border-gray-800 hover:bg-gray-200 dark:hover:bg-gray-800 text-gray-700 dark:text-gray-300 font-bold text-sm transition-colors cursor-pointer"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-6 py-3 rounded-2xl bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white font-extrabold text-sm shadow-md shadow-emerald-600/20 transition-all cursor-pointer"
            >
              Add Data
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

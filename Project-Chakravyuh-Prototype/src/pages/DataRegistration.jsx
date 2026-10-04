import React, { useState } from 'react';
import { UserPlus, CheckCircle2, Upload, PlusCircle, Shield } from 'lucide-react';
import { useApp } from '../context/AppContext';

export const DataRegistration = () => {
  const { addPerson, personnel = [], showToast } = useApp();

  const [formData, setFormData] = useState({
    id: '',
    name: '',
    department: 'Computer Science',
    role: 'Student',
    camera: 'CAM-01',
    status: 'Registered',
    avatar: '👨‍🎓',
    photoUrl: ''
  });

  const [imagePreview, setImagePreview] = useState(null);
  const [photoError, setPhotoError] = useState(null);
  const [successMessage, setSuccessMessage] = useState(null);

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
    setSuccessMessage(null);

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
      category,
      designation: formData.role,
      id: realId,
      badgeId: `BADGE-${realId}`
    });

    if (res && res.success) {
      setSuccessMessage(`Successfully registered ${formData.name} (${realId}) in database with photo image!`);
      setFormData({
        id: '',
        name: '',
        department: 'Computer Science',
        role: 'Student',
        camera: 'CAM-01',
        status: 'Registered',
        avatar: '👨‍🎓',
        photoUrl: ''
      });
      setImagePreview(null);
      setPhotoError(null);

      setTimeout(() => {
        setSuccessMessage(null);
      }, 4000);
    }
  };

  return (
    <div className="w-full space-y-6 select-none pb-12 text-slate-900">
      {/* Top Banner - 100% Full Width */}
      <div className="w-full bg-white border border-slate-200 rounded-2xl p-7 shadow-xs flex flex-col sm:flex-row sm:items-center justify-between gap-5">
        <div className="flex items-center gap-4">
          <div className="w-14 h-14 rounded-2xl bg-slate-900 flex items-center justify-center text-white shadow-xs">
            <UserPlus className="w-7 h-7 stroke-[2.5]" />
          </div>
          <div>
            <h1 className="text-3xl font-black text-slate-900 tracking-tight">Register New Data</h1>
            <p className="text-base font-semibold text-slate-600 mt-1">
              Centralized Data Enrollment Portal for Students, Faculties & Deans
            </p>
          </div>
        </div>
      </div>

      {successMessage && (
        <div className="w-full p-5 bg-emerald-50 border border-emerald-300 text-emerald-900 font-extrabold text-base rounded-2xl flex items-center gap-3 animate-in fade-in duration-200">
          <CheckCircle2 className="w-7 h-7 text-emerald-600 flex-shrink-0" />
          <span>{successMessage}</span>
        </div>
      )}

      {/* Main Registration Card - 100% Full Width */}
      <div className="w-full bg-white border border-slate-200 rounded-2xl p-8 shadow-xs">
        <form onSubmit={handleSubmit} className="space-y-7">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-slate-900 font-black text-base mb-2">
                Member Category / Role *
              </label>
              <select
                value={formData.role}
                onChange={(e) => setFormData({ ...formData, role: e.target.value })}
                className="w-full px-4 py-3.5 bg-slate-50 border border-slate-200 rounded-xl text-slate-900 font-black text-base focus:outline-none focus:ring-2 focus:ring-slate-900 focus:bg-white transition-all"
              >
                {memberTypes.map((m) => (
                  <option key={m} value={m}>
                    {m}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-slate-900 font-black text-base mb-2">
                ID / Roll No / Staff Code
              </label>
              <input
                type="text"
                value={formData.id}
                onChange={(e) => setFormData({ ...formData, id: e.target.value })}
                placeholder="e.g. STU-2026-101 (Auto generated if blank)"
                className="w-full px-4 py-3.5 bg-slate-50 border border-slate-200 rounded-xl text-slate-900 placeholder-slate-400 font-mono font-bold text-base focus:outline-none focus:ring-2 focus:ring-slate-900 focus:bg-white transition-all"
              />
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-slate-900 font-black text-base mb-2">
                Full Name *
              </label>
              <input
                type="text"
                required
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                placeholder="e.g. Om Tamrakar / Dr. Vikramaditya Rao"
                className="w-full px-4 py-3.5 bg-slate-50 border border-slate-200 rounded-xl text-slate-900 font-bold placeholder-slate-400 text-base focus:outline-none focus:ring-2 focus:ring-slate-900 focus:bg-white transition-all"
              />
            </div>

            <div>
              <label className="block text-slate-900 font-black text-base mb-2">
                Department / Class / Branch *
              </label>
              <input
                type="text"
                required
                value={formData.department}
                onChange={(e) => setFormData({ ...formData, department: e.target.value })}
                placeholder="e.g. BCA 2nd Year / Computer Science"
                className="w-full px-4 py-3.5 bg-slate-50 border border-slate-200 rounded-xl text-slate-900 font-bold placeholder-slate-400 text-base focus:outline-none focus:ring-2 focus:ring-slate-900 focus:bg-white transition-all"
              />
            </div>
          </div>

          {/* Photo Image Upload Section */}
          <div className="space-y-2">
            <label className="block text-slate-900 font-black text-base mb-2 flex items-center justify-between">
              <span>
                Upload Member Photo Image (For Facial Recognition Check-in) <span className="text-rose-500 font-extrabold">* (Mandatory)</span>
              </span>
              {photoError && <span className="text-xs text-rose-600 font-black animate-pulse">Photo Required!</span>}
            </label>
            <div className={`flex flex-col sm:flex-row items-center gap-5 p-5 rounded-2xl transition-all border ${
              photoError ? 'border-rose-500 bg-rose-50/60 ring-2 ring-rose-500/30' : 'bg-slate-50 border-slate-200'
            }`}>
              <div className="w-24 h-24 rounded-2xl bg-white border border-slate-300 overflow-hidden flex items-center justify-center text-4xl shadow-xs flex-shrink-0">
                {imagePreview || formData.photoUrl ? (
                  <img src={imagePreview || formData.photoUrl} alt="Member Preview" className="w-full h-full object-cover" />
                ) : (
                  <span className="text-slate-400">📷</span>
                )}
              </div>
              <div className="flex-1 w-full space-y-3">
                <input
                  type="file"
                  accept="image/*"
                  onChange={handleFileChange}
                  className="block w-full text-sm text-slate-700 file:mr-4 file:py-3 file:px-6 file:rounded-xl file:border-0 file:text-sm file:font-black file:bg-slate-900 file:text-white hover:file:bg-emerald-600 cursor-pointer transition-colors"
                />
                <input
                  type="url"
                  value={formData.photoUrl}
                  onChange={handleUrlChange}
                  placeholder="Or paste direct Photo URL link..."
                  className="w-full px-4 py-3 bg-white border border-slate-200 rounded-xl text-slate-900 placeholder-slate-400 text-sm font-semibold focus:outline-none focus:border-slate-400"
                />
              </div>
            </div>
            {photoError && (
              <p className="text-sm font-extrabold text-rose-600 bg-rose-100/90 p-3.5 rounded-xl border border-rose-200 flex items-center gap-2 animate-in fade-in">
                <span>⚠️ {photoError}</span>
              </p>
            )}
          </div>

          {/* Avatar Icon Selector */}
          <div>
            <label className="block text-slate-900 font-black text-base mb-3">
              Select Avatar Icon Fallback
            </label>
            <div className="flex items-center space-x-4 overflow-x-auto pb-2">
              {avatars.map((av) => (
                <button
                  type="button"
                  key={av}
                  onClick={() => setFormData({ ...formData, avatar: av })}
                  className={`w-14 h-14 rounded-2xl border text-3xl flex items-center justify-center transition-all cursor-pointer ${
                    formData.avatar === av
                      ? 'bg-slate-900 border-slate-900 text-white shadow-sm'
                      : 'bg-white border-slate-200 hover:border-slate-400'
                  }`}
                >
                  {av}
                </button>
              ))}
            </div>
          </div>

          {/* Submit Button */}
          <div className="pt-6 border-t border-slate-100 flex justify-end">
            <button
              type="submit"
              className="px-12 py-4 rounded-2xl bg-slate-900 hover:bg-emerald-600 text-white font-black text-base shadow-md transition-all cursor-pointer flex items-center gap-3"
            >
              <UserPlus className="w-6 h-6 stroke-[2.5]" />
              <span>Insert Member Data</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default DataRegistration;

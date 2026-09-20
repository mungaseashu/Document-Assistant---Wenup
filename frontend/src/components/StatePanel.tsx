import React, { useState } from 'react';
import { PersonalWishesState, FieldChange } from '../types';
import { EditFieldModal } from './EditFieldModal';

interface StatePanelProps {
  state: PersonalWishesState | null;
  onUpdateState: (changes: FieldChange[]) => void;
}

export const StatePanel: React.FC<StatePanelProps> = ({ state, onUpdateState }) => {
  const [editingField, setEditingField] = useState<{key: string, data: any} | null>(null);

  if (!state) {
    return (
      <div className="flex items-center justify-center h-full bg-white text-gray-400">
        Waiting for session to initialize...
      </div>
    );
  }

  const handleSave = (changes: FieldChange[]) => {
    onUpdateState(changes);
    setEditingField(null);
  };

  const fields = [
    { key: 'full_name', label: 'Full Name' },
    { key: 'home_address', label: 'Home Address' },
    { key: 'covers_worldwide_assets', label: 'Covers Worldwide Assets' },
    { key: 'has_children', label: 'Has Children' },
    { key: 'children_names', label: 'Children Names' },
    { key: 'executor_name', label: 'Executor Name' },
    { key: 'executor_relationship', label: 'Executor Relationship' },
    { key: 'specific_gifts', label: 'Specific Gifts' },
    { key: 'additional_wishes', label: 'Additional Wishes' },
  ] as const;

  const confirmedFields = fields.filter(f => {
    const fd = (state as any)[f.key];
    return fd && (fd.status === 'CONFIRMED' || fd.status === 'CORRECTED');
  });
  const pendingFields = fields.filter(f => !confirmedFields.includes(f));
  const percentage = Math.round((confirmedFields.length / fields.length) * 100) || 0;

  return (
    <div className="flex flex-col gap-4 shrink-0">
      {/* Progress Card */}
      <div className="bg-white p-5 rounded-3xl shadow-sm border border-[#E0E5F2] flex items-center gap-6 shrink-0">
        <div className="relative w-20 h-20 shrink-0">
           <svg className="w-full h-full transform -rotate-90" viewBox="0 0 100 100">
             <circle cx="50" cy="50" r="40" stroke="#F4F7FE" strokeWidth="12" fill="none" />
             <circle cx="50" cy="50" r="40" stroke="#05CD99" strokeWidth="12" fill="none" strokeDasharray={`${percentage * 2.51} 251`} strokeLinecap="round" className="transition-all duration-1000" />
           </svg>
           <div className="absolute inset-0 flex items-center justify-center font-bold text-lg text-[#2B3674]">{percentage}%</div>
        </div>
        <div>
          <h3 className="text-xl font-bold text-[#2B3674] mb-1">Your Progress</h3>
          <p className="text-[13px] font-bold text-[#2B3674]">{confirmedFields.length} of {fields.length} questions confirmed</p>
          <p className="text-[11px] font-medium text-[#A3AED0] mt-0.5">{percentage === 100 ? 'Ready to finalize! 🚀' : 'Almost there! 🎉'}</p>
        </div>
      </div>

      {/* State Split Cards */}
      <div className="flex flex-col xl:flex-row gap-4 shrink-0">
        {/* Collected */}
        <div className="flex-1 w-full bg-white p-5 rounded-3xl shadow-sm border border-[#E0E5F2] flex flex-col">
          <h3 className="font-bold text-[#2B3674] mb-4 flex items-center gap-3 text-[15px] shrink-0">
            <div className="bg-[#05CD99] text-white rounded-lg p-1.5 shadow-sm">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="3" d="M5 13l4 4L19 7"></path></svg>
            </div>
            Information Collected
          </h3>
          <div className="space-y-2">
            {confirmedFields.map(f => {
              const fd = (state as any)[f.key];
              const val = fd.value;
              return (
                <div key={f.key} className="flex items-center justify-between text-[13px] cursor-pointer hover:bg-slate-50 p-2 rounded-lg -mx-2 transition-colors" onClick={() => setEditingField({key: f.key, data: fd})}>
                  <div className="flex items-center gap-2 text-[#A3AED0] font-medium">
                    <div className="w-4 h-4 rounded-full bg-[#05CD99] flex items-center justify-center text-white shrink-0">
                      <svg className="w-2.5 h-2.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="3" d="M5 13l4 4L19 7"></path></svg>
                    </div>
                    {f.label}
                  </div>
                  <span className="font-bold text-[#2B3674] truncate max-w-[120px] text-right">
                    {val === true ? 'Yes' : val === false ? 'No' : Array.isArray(val) ? (val.length ? val.join(', ') : 'None') : String(val)}
                  </span>
                </div>
              )
            })}
          </div>
        </div>

        {/* Pending */}
        <div className="flex-1 w-full bg-white p-5 rounded-3xl shadow-sm border border-[#E0E5F2] flex flex-col">
          <h3 className="font-bold text-[#2B3674] mb-4 flex items-center gap-3 text-[15px] shrink-0">
            <div className="bg-[#FFB547] text-white rounded-lg p-1.5 shadow-sm">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 6h16M4 10h16M4 14h16M4 18h16"></path></svg>
            </div>
            Pending Information
          </h3>
          <div className="space-y-3">
            {pendingFields.map(f => (
              <div key={f.key} className="flex items-center gap-2 text-[13px] font-medium text-[#2B3674]">
                <div className="w-4 h-4 rounded-full border-2 border-[#A3AED0] shrink-0"></div>
                {f.label}
              </div>
            ))}
          </div>
        </div>
      </div>
      
      {editingField && (
        <EditFieldModal 
          fieldKey={editingField.key}
          fieldData={editingField.data}
          onClose={() => setEditingField(null)}
          onSave={handleSave}
        />
      )}
    </div>
  );
};

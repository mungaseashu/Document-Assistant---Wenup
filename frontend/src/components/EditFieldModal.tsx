import React, { useState } from 'react';
import { FieldStatus, FieldChange } from '../types';

interface EditFieldModalProps {
  fieldKey: string;
  fieldData: any;
  onClose: () => void;
  onSave: (changes: FieldChange[]) => void;
}

export const EditFieldModal: React.FC<EditFieldModalProps> = ({ fieldKey, fieldData, onClose, onSave }) => {
  const [value, setValue] = useState(
    fieldData.value !== null ? 
      (Array.isArray(fieldData.value) ? fieldData.value.join(', ') : String(fieldData.value)) 
      : ''
  );

  const handleSave = () => {
    let parsedValue: any = value;
    
    // Quick heuristic parsing for the known booleans and lists
    if (fieldKey === 'covers_worldwide_assets' || fieldKey === 'has_children') {
      parsedValue = value.toLowerCase() === 'true' || value.toLowerCase() === 'yes';
    } else if (fieldKey === 'children_names' || fieldKey === 'specific_gifts' || fieldKey === 'additional_wishes') {
      parsedValue = value.split(',').map((s: string) => s.trim()).filter(Boolean);
    }
    
    onSave([{
      field: fieldKey,
      proposed_value: parsedValue,
      status: FieldStatus.CORRECTED,
      confidence: 1.0,
      reason: 'Manual UI override'
    }]);
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 max-w-md w-full shadow-xl">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Edit {fieldKey.replace(/_/g, ' ')}</h3>
        
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-1">New Value</label>
          <input 
            type="text" 
            className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500"
            value={value}
            onChange={(e) => setValue(e.target.value)}
            placeholder="Enter value..."
          />
          <p className="text-xs text-gray-500 mt-2">
            For lists, separate with commas. For booleans, use yes/no or true/false.
          </p>
        </div>

        <div className="flex justify-end gap-2">
          <button onClick={onClose} className="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded-md">Cancel</button>
          <button onClick={handleSave} className="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700">Save</button>
        </div>
      </div>
    </div>
  );
};

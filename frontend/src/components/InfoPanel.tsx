import React from 'react';

interface InfoPanelProps {
  data: any;
  onClose: () => void;
}

export const InfoPanel: React.FC<InfoPanelProps> = ({ data, onClose }) => {
  if (!data) return null;

  return (
    <div className="absolute right-6 top-24 w-80 glass-panel rounded-2xl p-6 z-50 transition-all duration-300 animate-in slide-in-from-right">
      <div className="flex justify-between items-center mb-4 border-b border-white/10 pb-2">
        <h3 className="text-lg font-semibold text-blue-400">Node Details</h3>
        <button onClick={onClose} className="text-gray-400 hover:text-white transition-colors">
          ✕
        </button>
      </div>
      
      <div className="space-y-4 text-sm text-gray-300">
        <div>
          <span className="block text-gray-500 mb-1">Type</span>
          <span className="font-mono bg-black/30 px-2 py-1 rounded text-xs">
            {data.type}
          </span>
        </div>
        
        <div>
          <span className="block text-gray-500 mb-1">Code / ID</span>
          <span className="font-mono text-white">{data.label}</span>
        </div>

        {data.quantity && (
          <div>
            <span className="block text-gray-500 mb-1">Quantity / Stock</span>
            <span className="text-green-400 font-bold">{data.quantity}</span>
          </div>
        )}

        {data.status && (
          <div>
            <span className="block text-gray-500 mb-1">Status</span>
            <span className="text-blue-300">{data.status}</span>
          </div>
        )}
      </div>
    </div>
  );
};

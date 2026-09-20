import React from 'react';

interface ActivityFeedProps {
  activity: any[];
}

export const ActivityFeed: React.FC<ActivityFeedProps> = ({ activity }) => {
  if (!activity || activity.length === 0) return null;

  return (
    <div className="bg-white p-6 rounded-3xl shadow-sm border border-[#E0E5F2] flex flex-col h-full overflow-hidden">
      <div className="flex items-center justify-between mb-6 shrink-0">
         <h3 className="font-bold text-[#2B3674] flex items-center gap-3 text-lg">
           <div className="bg-[#4318FF] text-white rounded-lg p-1.5 shadow-sm">
             <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
           </div>
           Recent Activity
         </h3>
      </div>
      
      <div className="flex-1 overflow-y-auto custom-scrollbar pr-2">
        <div className="ml-2 border-l-2 border-[#E0E5F2] space-y-6 pb-4">
          {[...activity].reverse().map((entry, idx) => {
            const timeString = new Date(entry.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
            return (
              <div key={idx} className="relative pl-6">
                <div className="absolute -left-[7px] top-1 w-3 h-3 bg-[#4318FF] rounded-full ring-4 ring-white"></div>
                <div className="flex flex-col gap-0.5">
                  <span className="text-[#A3AED0] font-bold text-[12px]">{timeString}</span>
                  <p className="text-[#2B3674] text-[14px] leading-snug">
                    <span className="font-bold capitalize">{entry.field.replace(/_/g, ' ')}</span> updated 
                    <span className="text-[#A3AED0] ml-1 font-medium text-[13px]">
                      ({entry.proposed_value === true ? 'Yes' : entry.proposed_value === false ? 'No' : Array.isArray(entry.proposed_value) ? (entry.proposed_value.length ? entry.proposed_value.join(', ') : 'None') : String(entry.proposed_value)})
                    </span>
                  </p>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};

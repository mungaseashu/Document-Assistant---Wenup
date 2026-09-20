import React from 'react';
import ReactMarkdown from 'react-markdown';

interface DocumentPreviewProps {
  document: string;
}

export const DocumentPreview: React.FC<DocumentPreviewProps> = ({ document }) => {
  return (
    <div className="bg-white rounded-3xl shadow-sm border border-[#E0E5F2] flex flex-col shrink-0">
      <div className="p-5 border-b border-slate-50 flex items-center justify-between">
        <h3 className="font-bold text-[#2B3674] flex items-center gap-3 text-[15px]">
          <div className="bg-[#5B5CE6] text-white rounded-lg p-1.5 shadow-sm">
             <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4zm2 6a1 1 0 011-1h6a1 1 0 110 2H7a1 1 0 01-1-1zm1 3a1 1 0 100 2h6a1 1 0 100-2H7z" clipRule="evenodd" />
            </svg>
          </div>
          Live Document Preview
        </h3>
      </div>
      <div className="p-6 bg-[#F4F7FE]/50 rounded-b-3xl">
        <div className="bg-white p-8 shadow-sm border border-[#E0E5F2] prose prose-sm max-w-none rounded-2xl text-[#2B3674]">
          {document ? (
            <ReactMarkdown>{document}</ReactMarkdown>
          ) : (
            <div className="flex flex-col items-center justify-center py-10 opacity-50">
               <svg xmlns="http://www.w3.org/2000/svg" className="h-12 w-12 mb-3 text-[#A3AED0]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                 <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
               </svg>
               <p className="text-[#A3AED0] font-medium text-center">Document preview will build here as you provide information.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

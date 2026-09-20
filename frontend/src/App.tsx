import { useState } from 'react';
import { useSession } from './store/useSession';
import { ChatPanel } from './components/ChatPanel';
import { StatePanel } from './components/StatePanel';
import { ActivityFeed } from './components/ActivityFeed';
import { DocumentPreview } from './components/DocumentPreview';
import { AlertCircle, MessageSquare, Eye, Activity, FileText } from 'lucide-react';

function App() {
  const { messages, state, document, conflicts, activity, isLoading, error, sendMessage, updateStateField } = useSession();
  const [showDocModal, setShowDocModal] = useState(false);

  return (
    <div className="flex flex-col h-screen bg-[#F4F7FE] overflow-hidden font-sans">
      {/* Header */}
      <header className="bg-[#1B254B] text-white py-3 px-6 flex items-center justify-between shrink-0 z-20">
        <div className="flex items-center gap-4">
          <div className="bg-white text-[#5B5CE6] p-2 rounded-xl shadow-sm">
            <FileText className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-[22px] font-bold tracking-tight">Document Intake Assistant</h1>
            <p className="text-[#A3AED0] text-sm font-medium">Your guided assistant for creating your Personal Wishes Document</p>
          </div>
        </div>
      </header>

      {error && (
        <div className="bg-red-50 p-3 border-b border-red-200 flex items-center gap-2 text-red-700 shrink-0 z-10">
          <AlertCircle className="w-5 h-5" />
          <p className="text-sm font-medium">{error}</p>
        </div>
      )}

      <main className="flex-1 flex overflow-hidden p-4 gap-4 max-w-[1920px] mx-auto w-full">
        {/* Panel 1: Sidebar */}
        <div className="w-[140px] xl:w-[160px] bg-transparent flex flex-col gap-2 shrink-0 pt-2 hidden md:flex">
          <div className="px-3 py-3 rounded-xl flex items-center gap-3 font-bold transition-all bg-[#5B5CE6]/10 text-[#5B5CE6] cursor-default text-[15px]">
            <MessageSquare className="w-5 h-5" /> Chat
          </div>
          <div className="px-3 py-3 rounded-xl flex items-center gap-3 font-bold transition-all text-[#A3AED0] hover:bg-white/50 cursor-pointer text-[15px]" onClick={() => setShowDocModal(true)}>
            <Eye className="w-5 h-5" /> Preview
          </div>
          <div className="px-3 py-3 rounded-xl flex items-center gap-3 font-bold transition-all text-[#A3AED0] cursor-default text-[15px]">
            <Activity className="w-5 h-5" /> Activity
          </div>
        </div>

        {/* Panel 2: Chat Panel */}
        <div className="w-[350px] lg:w-[400px] xl:flex-[1.2] flex flex-col min-h-0 relative shrink-0">
          <ChatPanel 
            messages={messages} 
            isLoading={isLoading} 
            onSendMessage={sendMessage}
            conflicts={conflicts}
          />
        </div>

        {/* Panel 3: State & Progress Panel */}
        <div className="flex-[1.5] min-w-[350px] xl:min-w-[400px] flex flex-col min-h-0 gap-4 overflow-y-auto custom-scrollbar pr-2 pb-4">
          <StatePanel state={state} onUpdateState={updateStateField} />
          <DocumentPreview document={document} />
        </div>

        {/* Panel 4: Activity Panel */}
        <div className="w-[280px] xl:w-[320px] flex flex-col min-h-0 shrink-0 hidden lg:flex">
          <ActivityFeed activity={activity} />
        </div>
      </main>

      {/* Document Modal */}
      {showDocModal && (
        <div className="fixed inset-0 bg-[#1B254B]/60 backdrop-blur-sm z-50 flex items-center justify-center p-4 md:p-8" onClick={() => setShowDocModal(false)}>
          <div className="bg-white rounded-3xl shadow-2xl w-full max-w-4xl h-full flex flex-col overflow-hidden" onClick={e => e.stopPropagation()}>
            <div className="p-6 border-b border-slate-100 flex justify-between items-center bg-[#F4F7FE]">
              <h2 className="font-bold text-xl text-[#2B3674] flex items-center gap-3">
                 <FileText className="w-6 h-6 text-[#5B5CE6]" /> Document Preview
              </h2>
              <button onClick={() => setShowDocModal(false)} className="text-[#A3AED0] hover:text-[#2B3674] font-bold text-2xl">&times;</button>
            </div>
            <div className="flex-1 overflow-y-auto relative">
               <DocumentPreview document={document} />
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;

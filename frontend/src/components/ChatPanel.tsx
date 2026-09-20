import React, { useState, useEffect, useRef } from 'react';
import { Message } from '../types';
import { Send, Loader2, AlertCircle, Bot } from 'lucide-react';

interface ChatPanelProps {
  messages: Message[];
  isLoading: boolean;
  onSendMessage: (msg: string) => void;
  conflicts?: any[];
}

export const ChatPanel: React.FC<ChatPanelProps> = ({ messages, isLoading, onSendMessage, conflicts }) => {
  const [input, setInput] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, conflicts, isLoading]);

  const handleSend = () => {
    if (!input.trim() || isLoading) return;
    onSendMessage(input);
    setInput('');
  };

  return (
    <div className="flex flex-col h-full bg-white rounded-3xl overflow-hidden shadow-sm border border-slate-100">
      <div className="px-6 py-5 border-b border-slate-50 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <div className="bg-[#5B5CE6] text-white p-3 rounded-2xl shadow-sm">
            <Bot className="w-6 h-6" />
          </div>
          <div>
            <h2 className="text-lg font-bold text-[#2B3674]">Chat with Assistant</h2>
            <p className="text-sm text-[#A3AED0]">Let's create your Personal Wishes Document step by step.</p>
          </div>
        </div>
        <div className="flex items-center gap-2 px-3 py-1.5 bg-[#E6F8EF] text-[#05CD99] rounded-full text-xs font-bold">
          <div className="w-2 h-2 bg-[#05CD99] rounded-full"></div> Online
        </div>
      </div>
      
      <div className="flex-1 overflow-y-auto p-6 space-y-6 bg-white">
        {messages.map((msg, idx) => (
          <div key={idx} className={`flex gap-3 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            {msg.role === 'assistant' && (
              <div className="w-10 h-10 rounded-full bg-[#1B254B] flex items-center justify-center shrink-0 shadow-sm">
                <Bot className="w-5 h-5 text-white" />
              </div>
            )}
            <div className={`flex flex-col gap-1 max-w-[75%] ${msg.role === 'user' ? 'items-end' : 'items-start'}`}>
              <div className={`p-4 ${
                msg.role === 'user' 
                  ? 'bg-[#5B5CE6] text-white rounded-2xl rounded-tr-sm' 
                  : 'bg-[#F4F7FE] text-[#2B3674] rounded-2xl rounded-tl-sm'
              }`}>
                <p className="whitespace-pre-wrap text-[15px] font-medium leading-relaxed">{msg.content}</p>
              </div>
              <span className="text-[11px] text-[#A3AED0] font-medium px-1">08:06 AM</span>
            </div>
          </div>
        ))}
        {conflicts && conflicts.length > 0 && (
          <div className="flex justify-start gap-3">
             <div className="w-10 h-10 rounded-full bg-[#1B254B] flex items-center justify-center shrink-0 shadow-sm">
                <Bot className="w-5 h-5 text-white" />
             </div>
            <div className="max-w-[85%] rounded-2xl rounded-tl-sm p-4 bg-red-50 text-red-900 border border-red-100 shadow-sm">
              <h4 className="font-bold text-red-700 flex items-center gap-2 mb-3">
                <AlertCircle className="w-5 h-5" /> Potential conflict detected
              </h4>
              {conflicts.map((c, i) => (
                <div key={i} className="text-sm space-y-2 mb-3">
                  <p><span className="font-bold">Field:</span> {c.field}</p>
                  <p><span className="font-bold">Earlier information:</span> {String(c.previous_value)}</p>
                  <p><span className="font-bold">New information:</span> {String(c.proposed_value)}</p>
                  {c.reason && (
                    <p className="font-bold mt-2 bg-red-100/50 p-2 rounded-lg text-red-800">Reason: {c.reason}</p>
                  )}
                </div>
              ))}
              <p className="text-sm font-bold text-red-700 mt-2">Please clarify your choice.</p>
            </div>
          </div>
        )}
        {isLoading && (
          <div className="flex justify-start gap-3">
            <div className="w-10 h-10 rounded-full bg-[#1B254B] flex items-center justify-center shrink-0 shadow-sm">
                <Bot className="w-5 h-5 text-white" />
            </div>
            <div className="bg-[#F4F7FE] text-[#A3AED0] rounded-2xl rounded-tl-sm p-4 flex items-center gap-3 font-medium shadow-sm">
              <Loader2 className="w-5 h-5 animate-spin text-[#5B5CE6]" />
              <span>Thinking...</span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="p-5 bg-white">
        <div className="flex gap-3 border border-[#E0E5F2] rounded-2xl p-2 bg-white shadow-sm focus-within:border-[#5B5CE6] focus-within:ring-2 focus-within:ring-[#5B5CE6]/20 transition-all">
          <input
            type="text"
            className="flex-1 bg-transparent border-none px-4 py-2 focus:outline-none text-[#2B3674] placeholder-[#A3AED0] font-medium"
            placeholder="Type your response..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSend()}
            disabled={isLoading}
          />
          <button
            onClick={handleSend}
            disabled={isLoading || !input.trim()}
            className="bg-[#5B5CE6] text-white p-3 rounded-xl hover:bg-[#4318FF] disabled:opacity-50 flex items-center justify-center shadow-md transition-all"
          >
            <Send className="w-5 h-5" />
          </button>
        </div>
      </div>
    </div>
  );
};

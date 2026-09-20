import { useState, useCallback, useEffect } from 'react';
import { ApiClient } from '../api/client';
import { Message, PersonalWishesState, FieldChange } from '../types';

export function useSession() {
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [state, setState] = useState<PersonalWishesState | null>(null);
  const [document, setDocument] = useState<string>('');
  
  const [conflicts, setConflicts] = useState<any[]>([]);
  const [activity, setActivity] = useState<any[]>([]);
  
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const initSession = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);
      const id = await ApiClient.createSession();
      setSessionId(id);
      
      // Start conversation
      const msg: Message = { role: 'assistant', content: "Hello! I am the Document Intake Assistant. I'm here to help you draft your Personal Wishes Document. Let's start with your full name. What is your full name?" };
      setMessages([msg]);
    } catch (err: any) {
      setError(err.message || 'Network failure connecting to backend.');
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    initSession();
  }, [initSession]);

  const sendMessage = async (content: string) => {
    if (!sessionId) return;
    
    const userMsg: Message = { role: 'user', content };
    setMessages((prev) => [...prev, userMsg]);
    setIsLoading(true);
    setError(null);

    try {
      const res = await ApiClient.sendMessage(sessionId, content);
      setState(res.state);
      setDocument(res.document);
      if (res.conflicts) setConflicts(res.conflicts);
      if (res.recent_audit) setActivity((prev) => [...(res.recent_audit || []), ...prev]);
      setMessages((prev) => [...prev, { role: 'assistant', content: res.reply }]);
    } catch (err: any) {
      setError(err.message || 'Failed to communicate with the assistant.');
      setMessages((prev) => [...prev, { role: 'assistant', content: 'Sorry, I encountered an error. Please try again.' }]);
    } finally {
      setIsLoading(false);
    }
  };

  const updateStateField = async (changes: FieldChange[]) => {
    if (!sessionId) return;
    setIsLoading(true);
    setError(null);
    try {
      const { state: updatedState, recent_audit } = await ApiClient.updateState(sessionId, changes);
      setState(updatedState);
      if (recent_audit) setActivity((prev) => [...(recent_audit || []), ...prev]);
      
      const docRes = await fetch(`http://localhost:8000/api/sessions/${sessionId}/document`);
      if (docRes.ok) {
        const docData = await docRes.json();
        setDocument(docData.document);
      }
    } catch (err: any) {
      setError(err.message || 'Failed to update state manually.');
    } finally {
      setIsLoading(false);
    }
  };

  return {
    sessionId,
    messages,
    state,
    document,
    conflicts,
    activity,
    isLoading,
    error,
    sendMessage,
    updateStateField,
  };
}

import { OrchestrationAPIResponse, PersonalWishesState, FieldChange } from '../types';

const API_BASE = 'http://localhost:8000/api';

export class ApiClient {
  static async createSession(): Promise<string> {
    const res = await fetch(`${API_BASE}/sessions`, { method: 'POST' });
    if (!res.ok) throw new Error('Failed to create session');
    const data = await res.json();
    return data.session_id;
  }

  static async sendMessage(sessionId: string, content: string): Promise<OrchestrationAPIResponse> {
    const res = await fetch(`${API_BASE}/sessions/${sessionId}/messages`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ content }),
    });
    if (!res.ok) throw new Error('Failed to send message');
    return res.json();
  }

  static async updateState(sessionId: string, changes: FieldChange[]): Promise<{state: PersonalWishesState, recent_audit: any[]}> {
    const res = await fetch(`${API_BASE}/sessions/${sessionId}/state`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ changes }),
    });
    if (!res.ok) throw new Error('Failed to update state');
    return res.json();
  }
}

import type { AgentsData } from '../types';

const BASE = '/api';

export async function fetchAgents(): Promise<AgentsData | null> {
  try {
    const res = await fetch(`${BASE}/agents`, { signal: AbortSignal.timeout(5000) });
    if (!res.ok) return null;
    return res.json();
  } catch { return null; }
}

export async function checkHealth(): Promise<boolean> {
  try {
    const res = await fetch(`${BASE}/health`, { signal: AbortSignal.timeout(2000) });
    return res.ok;
  } catch { return false; }
}

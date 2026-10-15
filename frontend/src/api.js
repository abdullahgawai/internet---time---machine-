/**
 * API Client for Internet Time Machine
 */

const API_BASE = '/api';

export async function fetchSnapshots(url) {
  const params = new URLSearchParams({ url: url.trim() });
  const res = await fetch(`${API_BASE}/snapshots?${params.toString()}`);
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    const msg = errorData.error?.message || `Failed to fetch snapshots (HTTP ${res.status})`;
    throw new Error(msg);
  }
  return res.json();
}

export async function fetchMetadata(url, timestamp) {
  const params = new URLSearchParams({ url: url.trim(), timestamp: timestamp.trim() });
  const res = await fetch(`${API_BASE}/metadata?${params.toString()}`);
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    const msg = errorData.error?.message || `Failed to fetch metadata (HTTP ${res.status})`;
    throw new Error(msg);
  }
  return res.json();
}

export async function fetchComparison(url, ts1, ts2) {
  const params = new URLSearchParams({ 
    url: url.trim(), 
    ts1: ts1.trim(), 
    ts2: ts2.trim() 
  });
  const res = await fetch(`${API_BASE}/compare?${params.toString()}`);
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    const msg = errorData.error?.message || `Failed to compare snapshots (HTTP ${res.status})`;
    throw new Error(msg);
  }
  return res.json();
}

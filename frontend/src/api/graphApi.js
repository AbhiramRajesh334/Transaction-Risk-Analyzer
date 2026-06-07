// Minimal API client for fetching the full graph and stats

export async function fetchFullGraph() {
  const res = await fetch('/api/graph/full');
  if (!res.ok) throw new Error('Failed to fetch full graph');
  return res.json();
}

export async function fetchGraphStats() {
  const res = await fetch('/api/graph/stats');
  if (!res.ok) throw new Error('Failed to fetch graph stats');
  return res.json();
}

export async function fetchAccountDetails(accountId) {
  const res = await fetch(`/api/graph/account/${encodeURIComponent(accountId)}`);
  if (!res.ok) throw new Error('Failed to fetch account details');
  return res.json();
}

export async function fetchFundFlowPath(source, target, maxHops = 5) {
  const res = await fetch(`/api/graph/path/${encodeURIComponent(source)}/${encodeURIComponent(target)}?max_hops=${maxHops}`);
  if (!res.ok) throw new Error('Failed to fetch fund flow path');
  return res.json();
}

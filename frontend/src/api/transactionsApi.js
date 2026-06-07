export async function fetchRecentTransactions(limit = 20, afterId = null) {
  const params = new URLSearchParams({ limit: String(limit) });
  if (afterId) params.set('after_id', afterId);
  const response = await fetch(`/api/transactions/recent?${params.toString()}`);
  if (!response.ok) {
    throw new Error('Failed to fetch recent transactions');
  }
  return response.json();
}

export async function fetchAccountTimeline(accountId, limit = 50) {
  const response = await fetch(`/api/graph/timeline/${accountId}?limit=${limit}`);
  if (!response.ok) {
    throw new Error('Failed to fetch account timeline');
  }
  return response.json();
}

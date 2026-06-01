// API client for risk and explainability endpoints

async function handleResponse(response) {
  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || 'API request failed');
  }
  return response.json();
}

export async function fetchHighRiskAccounts(limit = 10) {
  const res = await fetch(`/api/risk/top-10?limit=${encodeURIComponent(limit)}`);
  return handleResponse(res);
}

export async function fetchRiskAccount(accountId) {
  const res = await fetch(`/api/risk/account/${encodeURIComponent(accountId)}`);
  return handleResponse(res);
}

export async function fetchExplainability(accountId) {
  const res = await fetch(`/api/explanations/account/${encodeURIComponent(accountId)}`);
  return handleResponse(res);
}

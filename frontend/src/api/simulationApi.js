export async function triggerLiveTick(count = 1) {
  const response = await fetch(`/api/simulation/live-tick?count=${count}`, { method: 'POST' });
  if (!response.ok) {
    throw new Error('Failed to trigger live transaction tick');
  }
  return response.json();
}

export async function resetDemoDataset() {
  const response = await fetch('/api/simulation/reset-demo', { method: 'POST' });
  if (!response.ok) {
    throw new Error('Failed to reset demo dataset');
  }
  return response.json();
}

export async function fetchEvaluationMetrics(threshold = 60) {
  const response = await fetch(`/api/evaluation/metrics?threshold=${threshold}`);
  if (!response.ok) {
    throw new Error('Failed to fetch evaluation metrics');
  }
  return response.json();
}

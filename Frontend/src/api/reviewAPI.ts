const BASE_URL = import.meta.env.VITE_API_BASE_URL || "https://df12-102-12-233-54.ngrok-free.app";

export async function analyzePullRequest(repo: string, pr_number: string, max_findings = 5) {
  const payload = {
    provider: "github",
    repo,
    pr_number,
    max_findings
  };

  const response = await fetch(`${BASE_URL}/review`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    throw new Error(`Error: ${response.status}`);
  }

  return response.json();
}

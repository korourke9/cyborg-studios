const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL?.replace(/\/$/, "") ??
  "http://localhost:8080";

export type ArtifactDetails = {
  id: string;
  type: string;
  payload: string;
  createdAt: number;
};

export type ProjectSummary = {
  id: string;
  prompt: string;
  status: string;
  createdAt: number;
  updatedAt: number;
};

export type ProjectDetails = {
  id: string;
  prompt: string;
  status: string;
  createdAt: number;
  updatedAt: number;
  artifacts: ArtifactDetails[];
};

export type CreateProjectResponse = {
  projectId: string;
  status: string;
};

export function gameLabel(prompt: string, maxLength = 36): string {
  const cleaned = prompt.trim().replace(/\s+/g, " ");
  if (cleaned.length <= maxLength) return cleaned;
  return `${cleaned.slice(0, maxLength - 1).trimEnd()}…`;
}

export async function createProject(
  prompt: string,
): Promise<CreateProjectResponse> {
  const response = await fetch(`${API_BASE_URL}/api/projects`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ prompt }),
  });
  if (!response.ok) {
    throw new Error(`Create project failed (${response.status})`);
  }
  return response.json() as Promise<CreateProjectResponse>;
}

export async function listProjects(): Promise<ProjectSummary[]> {
  const response = await fetch(`${API_BASE_URL}/api/projects`);
  if (!response.ok) {
    throw new Error(`List projects failed (${response.status})`);
  }
  return response.json() as Promise<ProjectSummary[]>;
}

export async function getProject(projectId: string): Promise<ProjectDetails> {
  const response = await fetch(`${API_BASE_URL}/api/projects/${projectId}`);
  if (!response.ok) {
    throw new Error(`Get project failed (${response.status})`);
  }
  return response.json() as Promise<ProjectDetails>;
}

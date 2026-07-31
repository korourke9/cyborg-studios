const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL?.replace(/\/$/, "") ??
  "http://localhost:8080";

export type ArtifactDetails = {
  id: string;
  type: string;
  payload: string;
  createdAt: number;
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

export async function fetchText(path: string): Promise<string> {
  const response = await fetch(`${API_BASE_URL}${path}`);
  if (!response.ok) {
    throw new Error(`Request failed (${response.status})`);
  }
  return response.text();
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

export async function getProject(projectId: string): Promise<ProjectDetails> {
  const response = await fetch(`${API_BASE_URL}/api/projects/${projectId}`);
  if (!response.ok) {
    throw new Error(`Get project failed (${response.status})`);
  }
  return response.json() as Promise<ProjectDetails>;
}

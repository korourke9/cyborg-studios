const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL?.replace(/\/$/, "") ??
  "http://localhost:8080";

export { API_BASE_URL };

export function gameBundleEntryUrl(projectId: string): string {
  return `${API_BASE_URL}/api/projects/${projectId}/bundle/entry.js`;
}

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

export class ApiError extends Error {
  readonly status: number;

  constructor(message: string, status: number) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

export function gameLabel(prompt: string, maxLength = 36): string {
  const cleaned = prompt.trim().replace(/\s+/g, " ");
  if (cleaned.length <= maxLength) return cleaned;
  return `${cleaned.slice(0, maxLength - 1).trimEnd()}…`;
}

async function readApiError(response: Response, fallback: string): Promise<ApiError> {
  try {
    const body = (await response.json()) as { message?: string; detail?: string };
    const message = body.message?.trim() || body.detail?.trim() || fallback;
    return new ApiError(message, response.status);
  } catch {
    return new ApiError(fallback, response.status);
  }
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
    throw await readApiError(
      response,
      `Create project failed (${response.status})`,
    );
  }
  return response.json() as Promise<CreateProjectResponse>;
}

export async function listProjects(): Promise<ProjectSummary[]> {
  const response = await fetch(`${API_BASE_URL}/api/projects`);
  if (!response.ok) {
    throw await readApiError(
      response,
      `List projects failed (${response.status})`,
    );
  }
  return response.json() as Promise<ProjectSummary[]>;
}

export async function getProject(projectId: string): Promise<ProjectDetails> {
  const response = await fetch(`${API_BASE_URL}/api/projects/${projectId}`);
  if (!response.ok) {
    throw await readApiError(
      response,
      `Get project failed (${response.status})`,
    );
  }
  return response.json() as Promise<ProjectDetails>;
}

export async function deleteProject(projectId: string): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/api/projects/${projectId}`, {
    method: "DELETE",
  });
  if (!response.ok) {
    throw await readApiError(
      response,
      `Delete project failed (${response.status})`,
    );
  }
}

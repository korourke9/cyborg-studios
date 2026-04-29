import { getApiBaseUrl } from './config';

export type ProjectStatus =
	| 'PENDING'
	| 'VISION_IN_PROGRESS'
	| 'VISION_DONE'
	| 'DESIGN_IN_PROGRESS'
	| 'DESIGN_DONE'
	| 'STORY_IN_PROGRESS'
	| 'STORY_DONE'
	| 'ART_IN_PROGRESS'
	| 'ART_DONE'
	| 'ENGINEERING_IN_PROGRESS'
	| 'ENGINEERING_DONE'
	| 'QA_IN_PROGRESS'
	| 'QA_DONE'
	| 'FINAL_REVIEW_IN_PROGRESS'
	| 'FINAL_REVIEW_DONE'
	| 'DONE'
	| 'FAILED';

export type Artifact = {
	id: string;
	type: string;
	payload: string;
	createdAt: number;
};

export type ProjectDetails = {
	id: string;
	prompt: string;
	status: ProjectStatus;
	createdAt: number;
	updatedAt: number;
	artifacts: Artifact[];
};

type CreateProjectResponse = {
	projectId: string;
	status: ProjectStatus;
};

function toUrl(path: string): string {
	return `${getApiBaseUrl()}${path.startsWith('/') ? path : `/${path}`}`;
}

async function parseJson<T>(res: Response): Promise<T> {
	if (!res.ok) {
		throw new Error(`API ${res.status}: ${res.statusText}`);
	}
	return (await res.json()) as T;
}

export async function fetchText(path: string): Promise<string> {
	const res = await fetch(toUrl(path));
	if (!res.ok) {
		throw new Error(`API ${res.status}: ${res.statusText}`);
	}
	return res.text();
}

export async function createProject(prompt: string): Promise<CreateProjectResponse> {
	const res = await fetch(toUrl('/api/projects'), {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json'
		},
		body: JSON.stringify({ prompt })
	});
	return parseJson<CreateProjectResponse>(res);
}

export async function getProject(projectId: string): Promise<ProjectDetails> {
	const res = await fetch(toUrl(`/api/projects/${projectId}`));
	return parseJson<ProjectDetails>(res);
}

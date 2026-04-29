/**
 * Base URL for the Spring Boot API (browser + server).
 * Set in Docker via `PUBLIC_API_BASE_URL` (see docker-compose).
 */
export function getApiBaseUrl(): string {
	const fromEnv = import.meta.env.PUBLIC_API_BASE_URL as string | undefined;
	if (fromEnv && fromEnv.length > 0) {
		return fromEnv.replace(/\/$/, '');
	}
	return 'http://localhost:8080';
}

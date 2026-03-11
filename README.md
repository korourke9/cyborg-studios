# Multi-Agent Video Game Builder

A multi-agent system that generates playable 2D platformer games from natural-language prompts. The backend orchestrates studio-style teams (Creative Director, Design, Story, Art, Engineering, QA, Director); the frontend shows progress and artifacts and runs the generated game in the browser via Phaser.

## For developers and AI agents

- **Design and tasks**: Read [docs/multi-agent-game-builder-design.md](docs/multi-agent-game-builder-design.md) before implementing features or changing architecture. It defines tech stack, application structure, team mapping, artifact model (including file/unstructured data via JSON references), agentic workflow, and the task breakdown.
- **Cursor rules**: Project rules live in [.cursor/rules/](.cursor/rules/). They encode design-and-architecture guidance, Kotlin/Spring Boot/Exposed conventions, agentic-teams patterns (contracts, reflection, LLM routing), and frontend standards (Svelte 5, SvelteKit). The design doc is the source of truth; rules summarize and enforce it.
- **Syncing rules**: To sync rules and docs between this repo and another location (e.g. a Cursor worktree or `~/.cursor/cyborg-studios`), use the [scripts/sync_rules](scripts/sync_rules) script. Run `./scripts/sync_rules` with no args for usage.

## Repo layout

- `backend/` — Kotlin, Spring Boot (API), Kotlin Exposed, PostgreSQL; agents and orchestration.
- `frontend/` — TypeScript, Svelte 5, SvelteKit, Tailwind; prompt UI, artifact viewer, Phaser game runner.
- `docs/` — Design document and any additional documentation.
- `scripts/` — Utilities (e.g. sync_rules for rules/docs sync).

## Running locally

- **Prerequisites**:
  - Docker and Docker Compose installed.
  - Java 21 (or a JDK supported by the backend `build.gradle.kts`).

- **1. Start App via Docker Compose**
  - From the repo root:
    - `docker compose up`

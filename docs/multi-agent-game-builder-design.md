# Multi-Agent Video Game Builder — Design and Task Breakdown

## 1. Tech choices


| Layer             | Choice                                                           | Rationale                                                                                                            |
| ----------------- | ---------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------- |
| **Frontend**      | TypeScript, Svelte 5 + SvelteKit, Tailwind, Vitest, Playwright   | Per your goals; SvelteKit for SSR/API routes and static export if needed; Playwright for E2E on prompt → play flow.  |
| **Backend**       | Kotlin, Spring Boot (API only), Kotlin Exposed (DSL), PostgreSQL | Per your goals; Exposed fits Kotlin-first and schema-in-code.                                                        |
| **Agent runtime** | Kotlin orchestrator calling LLM APIs                             | Use **Lang4j** (Java/Kotlin) or **Spring AI** for prompts and tool use from Kotlin; avoid a separate Python service. |
| **Game runtime**  | Phaser 3 (browser)                                               | Strong fit for 2D platformers; single-genre MVP keeps scope manageable.                                              |
| **Testing**       | Mockk + Strikt, Kotest (backend); Vitest + Playwright (frontend) | As specified.                                                                                                        |


**Other dependencies to add**

- **Backend**: Spring WebFlux or Web (REST), Spring AI or Lang4j, Exposed + JDBC driver for PostgreSQL, Flyway/Liquibase or Exposed migrations for schema.
- **Frontend**: Phaser 3 (only in the "game runner" surface that loads generated games), plus your existing stack.
- **Agents**: No separate framework beyond "agent" modules in Kotlin that call LLMs and produce/consume structured artifacts (JSON + text/code).

**LLM API**: Assume one primary provider (e.g. OpenAI) with API key in config; design so swapping provider is a small change.

---

## 2. Application architecture

High-level: **Browser** (SvelteKit) talks to **Spring Boot API**; API orchestrates **agents** and persists **artifacts** and **game bundle**; browser shows prompt UI, artifact viewer, and a **Phaser-based game runner** that loads the generated game.

- **Repo layout**: Single repo: `backend/` (Kotlin/Spring), `frontend/` (SvelteKit), `docs/` (this design).
- **API surface**: REST only; generation is **asynchronous** (POST creates project and starts orchestration, GET polls for status and artifacts).
- **Data ownership**: PostgreSQL holds **projects**, **artifacts** (all team outputs), and **game bundle**. For MVP, "user" can be anonymous or a single default user.

**Backend layering with studio teams (DDD/onion)**

- **Domain** (no team concepts): `domain.model` (e.g. `Project`, `Artifact`, `GameSpec`, `DesignPillars`, `MechanicsSpec`, `NarrativeSpec`, `ArtDirection`, `AssetList`, `GameBundle`, `QaIssues`, `CoherenceReview`), `domain.service` (`ProjectDomainService`, validators).
- **Application**:
  - `application.usecase`: `CreateProjectUseCase`, `GetProjectUseCase`, `GenerateGameUseCase` (or `RunPipelineUseCase`).
  - `application.orchestration`: `PipelineOrchestrator` (durable workflow/state machine over `ProjectStatus`).
  - `application.team.design`: `CreativeDirectorAgentService`, `DesignersAgentService`, optional `DesignTeamReflectionService`.
  - `application.team.story`: `WritersAgentService`, `StoryTeamReflectionService`.
  - `application.team.art`: `ArtTeamAgentService`, `ArtTeamReflectionService`.
  - `application.team.engineering`: `EngineersAgentService`, `EngineeringTeamReflectionService`.
  - `application.team.qa`: `QaAgentService`, optional `QaTeamReflectionService`.
  - `application.team.direction`: `DirectorAgentService`, `DirectionTeamReflectionService`.
- **Infrastructure**: `infrastructure.persistence` (Exposed tables, repositories), `infrastructure.llm` (LLM client implementations, routing), `infrastructure.gamebundle` (bundle storage), `infrastructure.config`.
- **Interfaces/adapters**: `interfaces.web` (REST controllers and DTOs), `interfaces.mappers`.

**Artifact storage**

- **Structured artifacts**: JSON in DB mapped to domain classes.
- **File / unstructured data** (images, audio, generated assets): Store binary files or blobs; **Artifact** records use type `BINARY_ASSET` and **payload is JSON with a reference** (e.g. `filePath`, `assetUrl`, `blobId`) so the rest of the system stays schema-driven. Other artifacts (e.g. `AssetList`) may contain arrays of `{ "id", "role", "fileRef" }` pointing to these binaries.
- **Game bundle**: Generated JS + assets; store as a bundle and serve via API (script tag + asset base URL).

---

## 3. User flows

**MVP (one-shot, with visible artifacts)**

1. User opens app, enters prompt (e.g. "Mario in the style of Ghibli meets Van Gogh"), triggers "Generate".
2. Backend runs pipeline asynchronously; frontend receives `projectId` and polls GET `/api/projects/:id` for status and artifacts.
3. As artifacts are ready, they appear in the UI (Vision, Pillars, Design, Story, Art, Engineering, QA, Director).
4. When pipeline finishes, "Play" is enabled; user clicks "Play" and the game runs via Phaser runner loading the generated bundle.
5. No edit/refinement in MVP; user can start a new prompt for a new game.

**Later (refinement)**  
User sees intermediate artifacts and can give feedback; backend creates a new version or project and agents use feedback to produce a new design/code pass.

---

## 4. Agentic workflows

**Single genre (2D platformer).** Pipeline: Creative Director → Designers → Writers → Art → Engineers → QA → Director.

**Teams and artifact ownership**

- **Design team** (`application.team.design`): VisionDoc, DesignPillars, MechanicsSpec, SystemsSpec.
- **Story team** (`application.team.story`): NarrativeSpec, QuestBeats.
- **Art team** (`application.team.art`): ArtDirection, AssetList, AssetPrompts; may create BINARY_ASSET artifacts (payload = JSON with file/blob reference).
- **Engineering team** (`application.team.engineering`): GameBundle.
- **QA team** (`application.team.qa`): QaIssues.
- **Direction team** (`application.team.direction`): CoherenceReview, DirectorNotes.

**Core artifact model**

- `Project`: id, prompt, status (PENDING | CREATIVE_DIRECTOR_IN_PROGRESS | CREATIVE_DIRECTOR_DONE | … | DONE | FAILED), createdAt, updatedAt.
- `Artifact`: id, projectId, type (VISION_DOC | DESIGN_PILLARS | MECHANICS_SPEC | SYSTEMS_SPEC | NARRATIVE_SPEC | QUEST_BEATS | ART_DIRECTION | ASSET_LIST | ASSET_PROMPTS | GAME_BUNDLE | QA_ISSUES | COHERENCE_REVIEW | DIRECTOR_NOTES | REFLECTION_NOTE | BINARY_ASSET), payload (JSON or JSON with file/blob reference for unstructured data), createdAt.

**Durable, resumable orchestration**

- Each step reads project and upstream artifacts, builds team-specific context, runs agent(s) with reflection (draft → critique → revise), then persists artifacts and updates `ProjectStatus` in a transaction.
- On crash, orchestrator resumes from latest non-terminal status. Failures set `FAILED` and may create a REFLECTION_NOTE.

**Internal team reflection**

- Every team uses **draft → critique → revise → finalize**. Critique checks alignment with DesignPillars and team charter; revision is LLM or deterministic; optionally persist REFLECTION_NOTE.

**Context provisioning**  
Per-team context builders assemble only the artifacts that team needs (see design doc for full list). For MVP, pass full artifacts.

**Multi-model routing**  
`ModelCapability` enum and `LlmRouter.forCapability(...)` return a configured `LlmModel`. Config maps capabilities (CREATIVE_DIRECTOR, DESIGN, WRITING, ART, ENGINEERING, QA, DIRECTOR) to model IDs so different roles can use different models later.

---

## 5. Task breakdown

Tasks are sized for one agent or human to implement and another to review. See full list in original plan; phases: Foundation (repo, backend skeleton, DB/Exposed, frontend skeleton) → Agents and orchestration (LLM router, each team's agents + reflection, orchestrator, REST API) → Frontend and play (prompt UI, project/status page, artifact viewer, game bundle serving, Phaser runner, Play button) → Quality and polish (backend tests, E2E, error handling).

---

## 6. Open decisions

- Async is default; implementation details (threading, queues) open.
- Game bundle: single JS file vs multi-file; multi-file may be better for large assets.
- Asset generation: MVP placeholders; later Art Team generates binaries, stored and referenced via JSON (e.g. BINARY_ASSET + AssetList entries with `fileRef`).

---

## 7. Studio teams and codebase mapping

- **Team** = logical owner of a subset of artifacts and prompts; implemented as package under `application.team.<name>` (agents, reflection services, helpers).
- **Template per team**: Inputs (which artifacts to read), Outputs (which artifacts to write), Quality bar, Internal process (at least one reflection round).
- **Mapping**: design → `application.team.design`, story → `application.team.story`, art → `application.team.art`, engineering → `application.team.engineering`, qa → `application.team.qa`, direction → `application.team.direction`. Art team may create BINARY_ASSET artifacts; payload is JSON with a reference to the file/blob.

---

## 8. Agent contracts and reflection pattern

- **Contracts**: Each agent output = domain data class in `domain.model`. Team packages define prompt template and JSON skeleton (including file refs: `assetFilePath`, `assetUrl`, `blobId`). Request JSON-only (or provider structured mode); parse and validate into domain classes.
- **Reflection**: draft → critique (structured JSON: issues, severity, suggestions) → revise (LLM or deterministic) → finalize; optionally persist REFLECTION_NOTE.

---

## 9. Workflow evolution, handling gaps, and conventions for AI development

- **Durability**: ProjectStatus and Artifact rows are source of truth. Steps with `*_DONE` do not re-run unless "re-run from here" is added. On failure: set FAILED, optionally REFLECTION_NOTE.
- **Extending pipeline**: Add artifacts in domain.model (with file refs if needed), extend ProjectStatus, add agent in correct `application.team.*`, wire in PipelineOrchestrator and context builders. Prefer additive changes.
- **Gaps**: Domain detail → use DesignPillars and artifacts, document in REFLECTION_NOTE. Architectural change → conform to DDD/onion (domain → application → infrastructure → interfaces; no domain → infrastructure). New artifact/team → update enum and this doc or REFLECTION_NOTE.
- **Conventions**: One coherent unit of work (one team agent+tests, one use case, one frontend feature). New team logic → `application.team.*`; new domain → `domain.model`/`domain.service`; new endpoints → `interfaces.web` + `application.usecase`. Each agent service: unit tests with mocked LlmModel/LlmRouter; orchestrator: integration-style test for status and persistence.
- **Multi-model**: New capability → extend ModelCapability and config; changing model for existing capability → keep contracts stable, update tests first.

---

## 10. Summary

- **Stack**: SvelteKit (Svelte 5) + Tailwind + Phaser 3 (frontend); Kotlin + Spring Boot + Exposed + PostgreSQL (backend); Lang4j or Spring AI for LLM.
- **Architecture**: Single repo, REST API, team-based agents in backend; frontend: prompt UI, artifact viewer, Phaser runner.
- **Flow**: User prompt → full studio pipeline → structured artifacts + file-backed assets (referenced by JSON) + game bundle → user sees artifacts and plays in browser.
- **Tasks**: Phased; each task implementable and reviewable in a focused pass.

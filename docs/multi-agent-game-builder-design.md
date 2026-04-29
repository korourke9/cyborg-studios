# Multi-Agent Video Game Builder — Design and Task Breakdown

## 1. Tech choices


| Layer                         | Choice                                                          | Rationale                                                                                                           |
| ----------------------------- | --------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------- |
| **Frontend**                  | TypeScript, Svelte 5 + SvelteKit, Tailwind, Vitest, Playwright  | Per your goals; SvelteKit for SSR/API routes and static export if needed; Playwright for E2E on prompt → play flow. |
| **Backend**                   | Kotlin, Spring Boot (API only), Kotlin Exposed (DSL), PostgreSQL | Per your goals; Exposed fits Kotlin-first and schema-in-code.                                                       |
| **Durable workflow harness**  | Temporal Java SDK, hosted from the Kotlin/Spring backend        | Durable, observable, resumable execution for long-running generation pipelines, retries, timers, and future signals. |
| **Agent graph framework**     | LangGraph4j, scoped inside bounded team activities              | Team reasoning is graph-shaped without making the whole app a graph runtime.                                        |
| **LLM/provider abstraction**  | Internal `LlmRouter`, `LlmModel`, `AgentGraph<I, O>` interfaces | Keeps provider SDKs and LangGraph4j out of domain/application contracts; model routing remains swappable.            |
| **Game runtime**              | Phaser 3 (browser)                                              | Strong fit for 2D platformers; single-genre MVP keeps scope manageable.                                             |
| **Testing**                   | Backend integration tests for workflow slices; Vitest + Playwright | The app is orchestration-heavy, so integration tests should verify API → workflow → artifacts.                    |


**Other dependencies to add**

- **Backend**: Spring Web (REST), Temporal Java SDK, LangGraph4j, Exposed + JDBC driver for PostgreSQL, Flyway/Liquibase or Exposed migrations for schema.
- **Frontend**: Phaser 3 (only in the "game runner" surface that loads generated games), plus your existing stack.
- **Agents**: Team modules in Kotlin own prompts, graph definitions, reflection, parsing, and validation. LangGraph4j is an implementation detail behind internal `AgentGraph<I, O>` style interfaces.

**LLM API**: Assume one primary provider (e.g. OpenAI) with API key in config; design so swapping provider is a small change through `LlmRouter` and `LlmModel`.

---

## 2. Application architecture

High-level: **Browser** (SvelteKit) talks to **Spring Boot API**; API starts a **Temporal workflow** for generation; Temporal activities run team services that call LLM/agent graphs and persist **artifacts** and the **game bundle**; browser shows prompt UI, artifact viewer, and a **Phaser-based game runner** that loads the generated game.

- **Repo layout**: Single repo: `backend/` (Kotlin/Spring), `frontend/` (SvelteKit), `docs/` (this design).
- **API surface**: REST only; generation is **asynchronous and durable** (POST creates project and starts a Temporal workflow, GET polls project status and artifacts from PostgreSQL).
- **Data ownership**: PostgreSQL holds **projects**, **artifacts** (all team outputs), and **game bundle**. For MVP, "user" can be anonymous or a single default user.

**Backend layering with studio teams (DDD/onion)**

- **Domain** (no team concepts, no Temporal/LangGraph/provider SDK imports): `domain.model` (e.g. `Project`, `Artifact`, `GameSpec`, `DesignPillars`, `MechanicsSpec`, `NarrativeSpec`, `ArtDirection`, `AssetList`, `GameBundle`, `QaIssues`, `CoherenceReview`), `domain.service` (`ProjectDomainService`, validators).
- **Application**:
  - `application.usecase`: `CreateProjectUseCase`, `GetProjectUseCase`, `GenerateGameUseCase` (or `RunPipelineUseCase`).
  - `application.orchestration`: `GameGenerationWorkflow` / workflow contract, activity contracts, and a small `PipelineOrchestrator`/starter facade that starts Temporal workflows from use cases or REST paths.
  - `application.team.design`: `CreativeDirectorAgentService`, `DesignersAgentService`, optional `DesignTeamReflectionService`.
  - `application.team.story`: `WritersAgentService`, `StoryTeamReflectionService`.
  - `application.team.art`: `ArtTeamAgentService`, `ArtTeamReflectionService`.
  - `application.team.engineering`: `EngineersAgentService`, `EngineeringTeamReflectionService`.
  - `application.team.qa`: `QaAgentService`, optional `QaTeamReflectionService`.
  - `application.team.direction`: `DirectorAgentService`, `DirectionTeamReflectionService`.
- **Infrastructure**: `infrastructure.persistence` (Exposed tables, repositories), `infrastructure.temporal` (Temporal client, worker, activity wiring), `infrastructure.llm` (LLM clients, LangGraph4j adapters, routing), `infrastructure.gamebundle` (bundle storage), `infrastructure.config`.
- **Interfaces/adapters**: `interfaces.web` (REST controllers and DTOs), `interfaces.mappers`.

**Artifact storage**

- **Structured artifacts**: JSON in DB mapped to domain classes.
- **File / unstructured data** (images, audio, generated assets): Store binary files or blobs; **Artifact** records use type `BINARY_ASSET` and **payload is JSON with a reference** (e.g. `filePath`, `assetUrl`, `blobId`) so the rest of the system stays schema-driven. Other artifacts (e.g. `AssetList`) may contain arrays of `{ "id", "role", "fileRef" }` pointing to these binaries.
- **Game bundle**: Generated JS + assets; store as a bundle and serve via API (script tag + asset base URL).

---

## 3. User flows

**MVP (one-shot, with visible artifacts)**

1. User opens app, enters prompt (e.g. "Mario in the style of Ghibli meets Van Gogh"), triggers "Generate".
2. Backend starts a Temporal workflow asynchronously; frontend receives `projectId` and polls GET `/api/projects/:id` for status and artifacts.
3. As artifacts are ready, they appear in the UI (Vision, Pillars, Design, Story, Art, Engineering, QA, Director).
4. When pipeline finishes, "Play" is enabled; user clicks "Play" and the game runs via Phaser runner loading the generated bundle.
5. No edit/refinement in MVP; user can start a new prompt for a new game.

**Later (refinement)**  
User sees intermediate artifacts and can give feedback; backend creates a new version or project and agents use feedback to produce a new design/code pass.

---

## 4. Agentic workflows

**Single genre (2D platformer).** Project-level pipeline: Creative Director → Designers → Writers → Art → Engineers → QA → Director.

There are two graph layers, and they must not duplicate each other:

- **Temporal workflow graph**: Owns the durable project pipeline, team ordering, retries, timers, crash recovery, and future user feedback signals.
- **LangGraph4j team graphs**: Own bounded, internal agent reasoning inside a team activity, such as draft → critique → revise → validate → finalize.

**Teams and artifact ownership**

- **Design team** (`application.team.design`): VisionDoc, DesignPillars, MechanicsSpec, SystemsSpec.
- **Story team** (`application.team.story`): NarrativeSpec, QuestBeats.
- **Art team** (`application.team.art`): ArtDirection, AssetList, AssetPrompts; may create BINARY_ASSET artifacts (payload = JSON with file/blob reference).
- **Engineering team** (`application.team.engineering`): GameBundle.
- **QA team** (`application.team.qa`): QaIssues.
- **Direction team** (`application.team.direction`): CoherenceReview, DirectorNotes.

**Core artifact model**

- `Project`: id, prompt, status (PENDING | stage-specific `*_IN_PROGRESS` / `*_DONE` values such as VISION_IN_PROGRESS and DESIGN_DONE | DONE | FAILED), createdAt, updatedAt.
- `Artifact`: id, projectId, type (VISION_DOC | DESIGN_PILLARS | MECHANICS_SPEC | SYSTEMS_SPEC | NARRATIVE_SPEC | QUEST_BEATS | ART_DIRECTION | ASSET_LIST | ASSET_PROMPTS | GAME_BUNDLE | QA_ISSUES | COHERENCE_REVIEW | DIRECTOR_NOTES | REFLECTION_NOTE | BINARY_ASSET), payload (JSON or JSON with file/blob reference for unstructured data), createdAt.

**Durable, resumable orchestration**

- Temporal is the durable harness. The workflow owns step ordering and retry policy, but workflow code must remain deterministic.
- Temporal activities perform non-deterministic work: repository calls, LLM calls, LangGraph4j execution, artifact persistence, and status updates.
- Each activity reads project and upstream artifacts, builds team-specific context, runs the team graph/agent(s), validates output, then persists artifacts and updates `ProjectStatus` in a transaction.
- PostgreSQL remains the user-facing source of truth for project status and artifacts; Temporal is the execution history and recovery system.
- On crash, Temporal resumes workflow execution. Failures set `FAILED` and may create a `REFLECTION_NOTE`.

**Internal team reflection**

- Every team uses **draft → critique → revise → validate → finalize**. This is modeled as a LangGraph4j graph behind an internal application interface, not as framework-specific domain logic.
- Critique checks alignment with DesignPillars and team charter; revision may be LLM-driven or deterministic; validation parses and checks the contract before artifacts are persisted. Optionally persist `REFLECTION_NOTE`.

**Context provisioning**  
Per-team context builders assemble only the artifacts that team needs (see design doc for full list). For MVP, pass full artifacts.

**Multi-model routing**  
`ModelCapability` enum and `LlmRouter.forCapability(...)` return a configured `LlmModel`. Config maps capabilities (CREATIVE_DIRECTOR, DESIGN, WRITING, ART, ENGINEERING, QA, DIRECTOR) to model IDs so different roles can use different models later. LangGraph4j nodes call `LlmModel` through this interface rather than provider SDKs directly.

---

## 5. Task breakdown

Tasks are sized for one agent or human to implement and another to review. Phases:

1. **Foundation**: repo, backend skeleton, DB/Exposed, frontend skeleton, Docker Compose.
2. **Durable workflow foundation**: add Temporal services to Compose, backend Temporal dependencies/config, workflow/activity contracts, worker startup, workflow starter, and integration tests that verify API → workflow → persisted status/artifacts.
3. **Agent graph foundation**: add internal `LlmModel`, `LlmRouter`, `ModelCapability`, and `AgentGraph<I, O>` boundaries; add LangGraph4j behind those boundaries for the first team graph.
4. **Teams and orchestration**: implement each team's activity + graph + reflection + validation; wire them into the Temporal workflow in pipeline order.
5. **Frontend and play**: prompt UI, project/status page, artifact viewer, game bundle serving, Phaser runner, Play button.
6. **Quality and polish**: integration tests for workflow slices, Playwright E2E, error handling, retry/timeout policy, operational docs.

---

## 6. Open decisions

- Temporal is the default durable async harness; tune task queues, retry policies, and worker deployment as the app grows.
- Game bundle: single JS file vs multi-file; multi-file may be better for large assets.
- Asset generation: MVP placeholders; later Art Team generates binaries, stored and referenced via JSON (e.g. BINARY_ASSET + AssetList entries with `fileRef`).

---

## 7. Studio teams and codebase mapping

- **Team** = logical owner of a subset of artifacts and prompts; implemented as package under `application.team.<name>` (agents, reflection services, graph contracts/helpers).
- **Template per team**: Inputs (which artifacts to read), Outputs (which artifacts to write), Quality bar, Internal process (at least one reflection round).
- **Mapping**: design → `application.team.design`, story → `application.team.story`, art → `application.team.art`, engineering → `application.team.engineering`, qa → `application.team.qa`, direction → `application.team.direction`. Art team may create BINARY_ASSET artifacts; payload is JSON with a reference to the file/blob.

---

## 8. Agent contracts and reflection pattern

- **Contracts**: Each agent output = domain data class in `domain.model`. Team packages define prompt template and JSON skeleton (including file refs: `assetFilePath`, `assetUrl`, `blobId`). Request JSON-only (or provider structured mode); parse and validate into domain classes.
- **Framework boundary**: Application code exposes stable interfaces such as `AgentGraph<I, O>`, `LlmModel`, and `LlmRouter`. LangGraph4j, provider SDKs, and Temporal clients live behind adapters and must not leak into domain models, REST DTOs, or persisted artifact contracts.
- **Reflection**: draft → critique (structured JSON: issues, severity, suggestions) → revise (LLM or deterministic) → validate → finalize; optionally persist `REFLECTION_NOTE`.

---

## 9. Workflow evolution, handling gaps, and conventions for AI development

- **Durability**: ProjectStatus and Artifact rows are the app/UI source of truth; Temporal workflow history is the execution/recovery source of truth. Steps with `*_DONE` do not re-run unless "re-run from here" is added. On failure: set FAILED, optionally REFLECTION_NOTE.
- **Extending pipeline**: Add artifacts in domain.model (with file refs if needed), extend ProjectStatus, add team activity/graph in correct `application.team.*`, wire activity into `GameGenerationWorkflow`, and update context builders. Prefer additive changes.
- **Gaps**: Domain detail → use DesignPillars and artifacts, document in REFLECTION_NOTE. Architectural change → conform to DDD/onion (domain → application → infrastructure → interfaces; no domain → infrastructure). New artifact/team → update enum and this doc or REFLECTION_NOTE.
- **Conventions**: One coherent unit of work (one team activity+graph+integration test, one use case, one frontend feature). New team logic → `application.team.*`; new domain → `domain.model`/`domain.service`; new endpoints → `interfaces.web` + `application.usecase`. Prefer integration tests for API → workflow/activity → persistence behavior, with mocked/fake LLMs where needed.
- **Multi-model**: New capability → extend ModelCapability and config; changing model for existing capability → keep contracts stable, update tests first.

---

## 10. Summary

- **Stack**: SvelteKit (Svelte 5) + Tailwind + Phaser 3 (frontend); Kotlin + Spring Boot + Exposed + PostgreSQL (backend); Temporal for durable workflows; LangGraph4j for bounded team agent graphs.
- **Architecture**: Single repo, REST API, Temporal-backed generation workflow, team-based activities/graphs in backend; frontend: prompt UI, artifact viewer, Phaser runner.
- **Flow**: User prompt → full studio pipeline → structured artifacts + file-backed assets (referenced by JSON) + game bundle → user sees artifacts and plays in browser.
- **Tasks**: Phased; each task implementable and reviewable in a focused pass.

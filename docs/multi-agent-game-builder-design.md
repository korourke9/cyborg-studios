# Multi-Agent Video Game Builder — Design and Task Breakdown

## 1. Tech choices


| Layer                         | Choice                                                                | Rationale                                                                                                              |
| ----------------------------- | --------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------- |
| **Frontend**                  | TypeScript, Next.js (App Router), Tailwind, Vitest, Playwright        | App Router for SSR/client components; Playwright for E2E on prompt → play flow.                                        |
| **Backend**                   | Python 3.12+, FastAPI, SQLAlchemy 2.0 (async), PostgreSQL, uv         | FastAPI for typed REST; SQLAlchemy async + asyncpg; uv for packaging.                                                  |
| **Durable workflow harness**  | Temporal Python SDK, hosted from the FastAPI backend process          | Durable, observable, resumable execution for long-running generation pipelines, retries, timers, and future signals.   |
| **Agent framework**           | PydanticAI (team agents); optional LangGraph adapter                  | Structured outputs + tools for team agents; frameworks stay behind team ports.                                         |
| **LLM/provider abstraction**  | Internal `LlmRouter`, `LlmModel`, `AgentGraph[I, O]` protocols        | Keeps provider SDKs and agent frameworks out of domain/application contracts; cloud and local models stay swappable. |
| **Game runtime**              | Phaser 3 (browser)                                                    | Strong fit for 2D platformers; single-genre MVP keeps scope manageable.                                                |
| **Testing**                   | Backend pytest integration tests for workflow slices; Playwright E2E  | The app is orchestration-heavy, so integration tests should verify API → workflow → artifacts.                        |


**Other dependencies to add**

- **Backend**: FastAPI, Temporal Python SDK, PydanticAI (agents), optional LangGraph, SQLAlchemy + asyncpg, optional Alembic for migrations later.
- **Frontend**: Next.js App Router — `/` prompt, `/projects/[id]` studio desk (Brief + Studio + Play CTA), `/projects/[id]/play` Phaser cabinet. See design doc §3 for artifact audience and retro-arcade visual direction.
- **Agents**: Team modules own prompts, contracts, and reflection shape. **PydanticAI** is the default infrastructure adapter behind team `*AgentGraph` ports (structured outputs). Optional adapters (LangGraph, raw `LlmModel` reflective loop) stay swappable.

**LLM backends**: Team/application code uses only `LlmRouter` / `LlmModel`. Provider SDKs and HTTP clients live under `orchestration.infrastructure.llm`. Supported out of the box: cloud OpenAI, and OpenAI-compatible local servers (Ollama, vLLM, LM Studio, etc.) via `LLM_PROVIDER` + optional `LLM_BASE_URL`. Adding another backend is an infrastructure adapter, not a team change.

---

## 2. Application architecture

High-level: **Browser** (Next.js) talks to **FastAPI**; API starts a **Temporal workflow** for generation; orchestration activities coordinate peer studio-team services that produce **artifacts** and the **game bundle**; browser shows prompt UI, artifact viewer, and a **Phaser-based game runner** that loads the generated game.

- **Repo layout**: Single repo: `backend/` (Python/FastAPI), `frontend/` (Next.js), `docs/` (this design).
- **API surface**: REST only; generation is **asynchronous and durable** (POST creates project and starts a Temporal workflow, GET polls project status and artifacts from PostgreSQL).
- **Data ownership**: PostgreSQL holds **projects**, **artifacts** (all team outputs), and **game bundle**. For MVP, "user" can be anonymous or a single default user.

**Backend modules as local onions**

There are no repo-wide top-level `domain`, `application`, `infrastructure`, or `interfaces` packages. Those layers exist **inside each backend module/bounded context**, scoped to that module's responsibility.

`orchestration` is a backend module under `gamebuilder`. It owns the durable game-generation workflow, project/artifact state, and related REST surface. Studio teams are **peers** to orchestration under `gamebuilder.team.<name>`; orchestration coordinates teams, but teams own the logic that produces their artifacts. Keep the root `gamebuilder` package for app bootstrap and truly cross-module concerns only.

- **Domain** (no team concepts, no Temporal/LangGraph/provider SDK imports): `orchestration.domain.model` (e.g. `Project`, `Artifact`, status/type enums), `orchestration.domain.service` (validators as needed). Team-specific output models live in `team.<name>.domain.model` (e.g. `DesignPillars`, `MechanicsSpec`).
- **Application**:
  - `orchestration.application.usecase`: `CreateProjectUseCase`, `GetProjectUseCase`, `StartProjectGenerationUseCase`, step use cases (e.g. `RunVisionStepUseCase`), `FailProjectUseCase`.
  - `orchestration.application.port`: framework-neutral ports such as `GenerationWorkflowRunner`; no FastAPI, Temporal, LangGraph, or provider SDK imports.
- **Infrastructure**: `orchestration.infrastructure.persistence` (SQLAlchemy models, repositories), `orchestration.infrastructure.temporal` (workflow/activity definitions, client/worker wiring, workflow-runner adapter), `orchestration.infrastructure.llm` (provider adapters implementing `LlmModel` / `LlmRouter` only), `orchestration.infrastructure.gamebundle` (bundle storage), `orchestration.infrastructure.config`.
- **Interfaces/adapters**: `orchestration.interfaces.web` (REST routers and DTOs).
- **Studio teams** (each with its own local onion as needed):
  - `team.design.domain`, `team.design.application`, `team.design.infrastructure`: `DesignersAgentService`, `DesignReflectionProcess`, `DesignAgentGraph` implementations (reflective default; optional LangGraph adapter; deterministic stub).
  - `team.story.domain`, `team.story.application`, `team.story.infrastructure`: `WritersAgentService`, story reflection.
  - `team.art.domain`, `team.art.application`, `team.art.infrastructure`: `ArtTeamAgentService`, art reflection.
  - `team.engineering.domain`, `team.engineering.application`, `team.engineering.infrastructure`: `EngineersAgentService`, engineering reflection.
  - `team.qa.domain`, `team.qa.application`, `team.qa.infrastructure`: `QaAgentService`, optional QA reflection.
  - `team.producer.domain`, `team.producer.application`, `team.producer.infrastructure`: `ProducerAgentService`, producer reflection (coherence / ship call).

**Artifact storage**

- **Structured artifacts**: JSON in DB mapped to domain models (Pydantic or dataclasses in domain; persistence mapping in infrastructure).
- **File / unstructured data** (images, audio, generated assets): Store binary files or blobs; **Artifact** records use type `BINARY_ASSET` and **payload is JSON with a reference** (e.g. `filePath`, `assetUrl`, `blobId`) so the rest of the system stays schema-driven. Other artifacts (e.g. `AssetList`) may contain arrays of `{ "id", "role", "fileRef" }` pointing to these binaries.
- **Game bundle**: Generated JS + assets; store as a bundle and serve via API (script tag + asset base URL).

---

## 3. User flows and product UI

### Surfaces (information architecture)

App chrome uses a **left sidebar** (Cursor / Vercel / Notion–style): **+ New game** at the top, then a **Games** list sorted by last activity (`updatedAt`), labeled by a short name derived from the prompt.

| Route | Role |
| ----- | ---- |
| `/` | New game prompt. Brand-first; start generation. |
| `/projects/[id]` | **Project card**: prompt, inline brief (vision + pillars), pipeline stage buttons, Play. Clicking a stage reveals that team’s deliverables in the card. |
| `/projects/[id]/play` | **Play**: full-bleed Phaser runner (no sidebar). “Back to project” returns to the desk. |

```text
sidebar: New game | Games…
/  →  /projects/:id  ⇄  /projects/:id/play
```

API: `GET /api/projects` returns summaries (newest activity first) for the sidebar; `GET /api/projects/:id` remains the full project + artifacts poll.

### MVP flow (one-shot, visible artifacts)

1. User opens `/` (or **+ New game**), enters a prompt, starts generation.
2. Backend starts a Temporal workflow; frontend navigates to `/projects/:id` and polls GET `/api/projects/:id`.
3. Project card shows status + brief as Design finishes. Stage buttons open that team’s deliverables (empty until the team runs).
4. When `GAME_BUNDLE` exists, **Play** is enabled → `/projects/:id/play`.
5. MVP has no edit/refinement; create another game from the sidebar.

### Later (refinement)

- Per-artifact feedback / edit on primary targets (Vision, Pillars, Mechanics, Narrative, ArtDirection).
- Backend re-runs **from that team step** (Temporal), not only full silent regen.
- AssetPrompts, raw GameBundle payload, and REFLECTION_NOTE are not primary edit surfaces.

### Artifact audience (what users see)

Intent → story → look → **play**. Keep explanatory copy minimal — the layout should be self-explanatory.

| Priority | Artifacts | Presentation |
| -------- | --------- | ------------ |
| **Brief (in project card)** | VisionDoc summary, DesignPillars | Always visible on the card when present |
| **Stage deliverables** | MechanicsSpec, SystemsSpec, NarrativeSpec, ExperienceMilestones, ArtDirection, AssetList, AssetPrompts, QaIssues, CoherenceReview, ProducerNotes | Shown only for the selected pipeline stage button |
| **Play (not a JSON card)** | GameBundle | Play control / play route only |
| **Hidden** | REFLECTION_NOTE; raw GameBundle JSON | Not in the default desk UI |

### Project card layout

1. Title (short prompt label), full prompt, status, Play.
2. Brief strip: vision summary + pillar chips.
3. Pipeline stage buttons (Design → … → Producer); selected stage reveals deliverables below.
4. No separate “studio wall” of every artifact at once.

### Visual direction

Whimsical **retro game / arcade studio** vibe — playful, not corporate SaaS:

- Expressive pixel display type for brand and key labels; readable sans for body copy.
- Light **orange-cream** field with soft **lavender / light purple** accents, chunky borders, and a subtle grid.
- Motion: light press/start button feedback, status pulse while generating — presence, not noise.
- Play route stays visually quiet around the canvas so the game is the hero.
- Prefer short UI labels over instructional paragraphs.

---

## 4. Agentic workflows

**Single genre (2D platformer).** Project-level pipeline: Design (includes vision) → Writers → Art → Engineers → QA → Producer.

There are two control layers, and they must not duplicate each other:

- **Temporal workflow**: Owns the durable project pipeline, team ordering, retries, timers, crash recovery, and future user feedback signals. It coordinates teams but does not contain team logic.
- **Team reflection process**: Owns bounded, internal agent reasoning inside a team activity, such as draft → critique → revise → validate → finalize. Contracts and prompts live in team **application**; **PydanticAI** (default) and other frameworks live in team **infrastructure** behind `AgentGraph` / team-specific ports.

**Teams and artifact ownership**

- **Design team** (`team.design.*`): VisionDoc, DesignPillars, MechanicsSpec, SystemsSpec. Early creative vision lives here (no separate Creative Director team).
- **Story team** (`team.story.*`): NarrativeSpec, ExperienceMilestones (ordered player-experience milestones).
- **Art team** (`team.art.*`): ArtDirection (concept brief: hero/world/key scenes), AssetList, AssetPrompts; may create BINARY_ASSET artifacts later (payload = JSON with file/blob reference). MVP uses placeholder `fileRef`s — no generated images yet.
- **Engineering team** (`team.engineering.*`): GameBundle — structured Phaser 3 level (platforms, goal, palette hexes) plus compiled `entrySource` JS. Served at `GET /api/projects/{id}/bundle/entry.js` for the play cabinet.
- **QA team** (`team.qa.*`): QaIssues — structured review of GameBundle vs vision/core loop/milestones (verdict, severities, suggested fix team). MVP uses static checks + LLM reflection; gameplay sim / play telemetry later.
- **Producer team** (`team.producer.*`): CoherenceReview + ProducerNotes (`ship` | `revise` | `cut`) across vision/story/art/build/QA. MVP is a recommendation only — human approval / Temporal feedback signals still to come.

**Core artifact model**

- `Project`: id, prompt, status (PENDING | stage-specific `*_IN_PROGRESS` / `*_DONE` values such as VISION_IN_PROGRESS, DESIGN_DONE, PRODUCER_DONE | DONE | FAILED), createdAt, updatedAt.
- `Artifact`: id, projectId, type (VISION_DOC | DESIGN_PILLARS | MECHANICS_SPEC | SYSTEMS_SPEC | NARRATIVE_SPEC | EXPERIENCE_MILESTONES | ART_DIRECTION | ASSET_LIST | ASSET_PROMPTS | GAME_BUNDLE | QA_ISSUES | COHERENCE_REVIEW | PRODUCER_NOTES | REFLECTION_NOTE | BINARY_ASSET), payload (JSON or JSON with file/blob reference for unstructured data), createdAt.

**Durable, resumable orchestration**

- Temporal is the durable harness. The workflow owns step ordering and retry policy, but workflow code must remain deterministic.
- Temporal activities perform non-deterministic work: repository calls, calls into peer team services/graphs, artifact persistence, and status updates.
- Each activity reads project and upstream artifacts, builds team-specific context, calls the appropriate peer team service/graph, validates output, then persists artifacts and updates `ProjectStatus` **in a single Unit of Work transaction**.
- PostgreSQL remains the user-facing source of truth for project status and artifacts; Temporal is the execution history and recovery system.
- On crash, Temporal resumes workflow execution. Failures set `FAILED` and may create a `REFLECTION_NOTE`.

**Internal team reflection**

- Every team uses **draft → critique → revise → validate → finalize**. Output contracts and prompts live in team application (e.g. `DesignArtifactBundle`, `CritiqueResult`). The default live adapter is **PydanticAI** (`PydanticAIDesignAgentGraph`). Alternate adapters: raw `LlmModel` reflective loop, optional LangGraph, and deterministic stub.
- Critique checks alignment with DesignPillars and team charter; revision may be LLM-driven or deterministic; validation parses and checks the contract before artifacts are persisted. Optionally persist `REFLECTION_NOTE`.

**Context provisioning**  
Per-team context builders assemble only the artifacts that team needs. For MVP, pass full artifacts.

**Multi-model routing**  
`ModelCapability` enum and `LlmRouter.for_capability(...)` return a configured `LlmModel`. Config maps capabilities (DESIGN, WRITING, ART, ENGINEERING, QA, PRODUCER) to model IDs via transport-agnostic settings (`LLM_PROVIDER`, `LLM_BASE_URL`, `LLM_API_KEY`, `LLM_MODEL_*`). Team process code calls `LlmModel` rather than provider SDKs or HTTP clients directly.

---

## 5. Task breakdown

Tasks are sized for one agent or human to implement and another to review. Phases:

1. **Foundation** *(done — rebuilt on Python/FastAPI + Next.js)*: repo, backend skeleton, DB/SQLAlchemy, frontend skeleton, Docker Compose.
2. **Durable workflow foundation** *(done — rebuilt on Temporal Python SDK)*: Temporal in Compose, workflow/activity contracts, worker startup, workflow starter, integration tests for API → workflow → persisted status/artifacts.
3. **Agent graph foundation** *(done)*: `LlmModel`, `LlmRouter`, `ModelCapability`, `AgentGraph[I, O]`; design contracts in application; **PydanticAI** default agent adapter; optional reflective/`LlmModel` and LangGraph adapters; deterministic fallback; transport-agnostic LLM config (cloud + local).
4. **Teams and orchestration** *(done for MVP team set)*: Design → Story → Art → Engineering → QA → Producer wired in Temporal.
5. **Frontend and play** *(in progress)*: studio desk with sidebar + project card; GameBundle script serving; Phaser cabinet on `/projects/[id]/play`.
6. **Quality and polish**: more workflow-slice integration tests, Playwright E2E (prompt → desk → play), error handling, retry/timeout policy, operational docs.

---

## 6. Open decisions

- Temporal is the default durable async harness; tune task queues, retry policies, and worker deployment as the app grows.
- **Game bundle**: MVP stores a single `GAME_BUNDLE` JSON artifact with level geometry + compiled Phaser `entrySource`; API serves the script (`/bundle/entry.js`). Multi-file asset packs can come later.
- Asset generation: MVP placeholders; later Art Team generates binaries, stored and referenced via JSON (e.g. BINARY_ASSET + AssetList entries with `fileRef`).
- Schema migrations: create-tables-on-startup for early parity; introduce Alembic when schema churn warrants it.

---

## 7. Studio teams and codebase mapping

- **Team** = logical owner of a subset of artifacts and prompts; implemented as peer modules under `team.<name>`, not under `orchestration`. Each team may have its own `domain`, `application`, `infrastructure`, and `interfaces` packages scoped to that team's responsibilities.
- **Template per team**: Inputs (which artifacts to read), Outputs (which artifacts to write), Quality bar, Internal process (at least one reflection round).
- **Mapping**: design → `team.design.*`, story → `team.story.*`, art → `team.art.*`, engineering → `team.engineering.*`, qa → `team.qa.*`, producer → `team.producer.*`. Art team may create BINARY_ASSET artifacts; payload is JSON with a reference to the file/blob.

---

## 8. Agent contracts and reflection pattern

- **Contracts**: Each agent output = a domain model owned by the responsible module (for example `team.design.domain.model.DesignPillars` or orchestration-owned project/artifact state in `orchestration.domain.model`). Team packages define prompt template and JSON skeleton (including file refs: `assetFilePath`, `assetUrl`, `blobId`). Request JSON-only (or provider structured mode); parse and validate into domain models.
- **Framework boundary**: Team application owns contracts/prompts. Stable ports include `AgentGraph[I, O]`, `LlmModel`, `LlmRouter`, and workflow-runner ports. **PydanticAI** is the preferred agent adapter in team infrastructure; LangGraph/`LlmModel` loops remain optional. FastAPI, Temporal, PydanticAI, LangGraph, and provider SDKs must not leak into domain models, application use cases/ports, REST DTOs, or persisted artifact contracts.
- **Reflection**: draft → critique (structured JSON: issues, severity, suggestions) → revise → validate → finalize; optionally persist `REFLECTION_NOTE`.

---

## 9. Workflow evolution, handling gaps, and conventions for AI development

- **Durability**: ProjectStatus and Artifact rows are the app/UI source of truth; Temporal workflow history is the execution/recovery source of truth. Steps with `*_DONE` do not re-run unless "re-run from here" is added. On failure: set FAILED, optionally REFLECTION_NOTE.
- **Extending pipeline**: Add team-owned output models in the relevant `team.<name>.domain.model` when they are team-specific; add orchestration-owned project/artifact state in `orchestration.domain.model`; extend ProjectStatus; add artifact-producing team service/graph in correct `team.<name>.application`; wire Temporal workflow/activity adapters in `orchestration.infrastructure.temporal` to plain application use cases/ports; update context builders. Prefer additive changes.
- **Gaps**: Domain detail → use DesignPillars and artifacts, document in REFLECTION_NOTE. Architectural change → conform to the local onion of the module being changed (`<module>.domain` → `<module>.application` → `<module>.infrastructure` / `<module>.interfaces`; no domain → infrastructure). New artifact/team → update enum and this doc or REFLECTION_NOTE.
- **Conventions**: One coherent unit of work (one team service/graph+integration test, one use case, one frontend feature). New team logic → `team.<name>.application` with team-specific domain in `team.<name>.domain`; new orchestration domain → `orchestration.domain.model`/`orchestration.domain.service`; new endpoints → `orchestration.interfaces.web` + `orchestration.application.usecase`. Prefer integration tests for API → workflow/activity → team service → persistence behavior, with mocked/fake LLMs where needed.
- **Multi-model**: New capability → extend ModelCapability and config; changing model for existing capability → keep contracts stable, update tests first.

---

## 10. Summary

- **Stack**: Next.js (App Router) + Tailwind + Phaser 3 (frontend); Python + FastAPI + SQLAlchemy + PostgreSQL (backend); Temporal for durable workflows; PydanticAI for team agents (optional LangGraph / raw LLM adapters).
- **Architecture**: Single repo, REST API, Temporal-backed orchestration coordinating peer team services in backend; frontend: prompt → studio desk (brief + artifacts) → Phaser play route.
- **Flow**: User prompt → studio pipeline (Design → Story → Art → Engineering → QA → Producer) → structured artifacts + file-backed assets + game bundle → user inspects Brief/Studio on the desk and plays in `/projects/:id/play`.
- **Tasks**: Phased; each task implementable and reviewable in a focused pass. Phases 1–3 done on the current stack; Phase 4 (remaining teams) and Phase 5 (desk + play UI) are next.

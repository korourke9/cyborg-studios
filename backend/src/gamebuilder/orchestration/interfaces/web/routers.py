from uuid import UUID

from fastapi import APIRouter, Query, Request, status
from fastapi.responses import PlainTextResponse, Response

from gamebuilder.orchestration.application.usecase.get_project import ProjectDetails
from gamebuilder.orchestration.domain.model.project import Project
from gamebuilder.orchestration.interfaces.web.dtos import (
    ArtifactResponse,
    CreateProjectRequest,
    CreateProjectResponse,
    EngineeringLabOptionsResponse,
    EngineeringLabOptionsUpdateRequest,
    PlayBundleInfoResponse,
    ProjectResponse,
    ProjectSummaryResponse,
)

router = APIRouter()


def _to_project_response(details: ProjectDetails) -> ProjectResponse:
    project = details.project
    return ProjectResponse(
        id=project.id,
        prompt=project.prompt,
        status=project.status.value,
        created_at=project.created_at,
        updated_at=project.updated_at,
        artifacts=[
            ArtifactResponse(
                id=artifact.id,
                type=artifact.type.value,
                payload=artifact.payload,
                created_at=artifact.created_at,
            )
            for artifact in details.artifacts
        ],
    )


def _to_summary(project: Project) -> ProjectSummaryResponse:
    return ProjectSummaryResponse(
        id=project.id,
        prompt=project.prompt,
        status=project.status.value,
        created_at=project.created_at,
        updated_at=project.updated_at,
    )


@router.post(
    "/api/projects",
    response_model=CreateProjectResponse,
    status_code=status.HTTP_202_ACCEPTED,
    response_model_by_alias=True,
)
async def create_project(body: CreateProjectRequest, request: Request) -> CreateProjectResponse:
    container = request.app.state.container
    project = await container.create_project.execute(body.prompt)
    await container.start_project_generation.execute(project.id)
    return CreateProjectResponse(project_id=project.id, status=project.status.value)


@router.get(
    "/api/projects",
    response_model=list[ProjectSummaryResponse],
    response_model_by_alias=True,
)
async def list_projects(request: Request) -> list[ProjectSummaryResponse]:
    container = request.app.state.container
    projects = await container.list_projects.execute()
    return [_to_summary(project) for project in projects]


@router.get(
    "/api/projects/{project_id}",
    response_model=ProjectResponse,
    response_model_by_alias=True,
)
async def get_project(project_id: UUID, request: Request) -> ProjectResponse:
    container = request.app.state.container
    details = await container.get_project.execute(project_id)
    return _to_project_response(details)


@router.delete(
    "/api/projects/{project_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_project(project_id: UUID, request: Request) -> Response:
    container = request.app.state.container
    await container.delete_project.execute(project_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get(
    "/api/projects/{project_id}/bundle/entry.js",
    response_class=PlainTextResponse,
)
async def get_game_bundle_entry(
    project_id: UUID,
    request: Request,
    runtime: str = Query(default="ir"),
) -> PlainTextResponse:
    container = request.app.state.container
    source = await container.get_game_bundle_script.execute(
        project_id, runtime=runtime
    )
    return PlainTextResponse(
        content=source,
        media_type="application/javascript; charset=utf-8",
        headers={"Cache-Control": "no-store"},
    )


@router.get(
    "/api/projects/{project_id}/play",
    response_model=PlayBundleInfoResponse,
    response_model_by_alias=True,
)
async def get_play_bundle_info(
    project_id: UUID, request: Request
) -> PlayBundleInfoResponse:
    container = request.app.state.container
    info = await container.get_play_bundle_info.execute(project_id)
    return PlayBundleInfoResponse(
        project_id=info.project_id,
        title=info.title,
        runtimes=info.runtimes,
        sdk_review_verdict=info.sdk_review_verdict,
        sdk_review_notes=info.sdk_review_notes,
        implemented=info.implemented,
    )


@router.get("/api/projects/{project_id}/assets/{asset_id}")
async def get_project_asset(
    project_id: UUID, asset_id: str, request: Request
) -> Response:
    container = request.app.state.container
    data, content_type = await container.get_project_asset.execute(project_id, asset_id)
    return Response(
        content=data,
        media_type=content_type,
        headers={"Cache-Control": "public, max-age=3600"},
    )


# TEMP: remove before external release
@router.get(
    "/api/lab/engineering",
    response_model=EngineeringLabOptionsResponse,
    response_model_by_alias=True,
)
async def get_engineering_lab_options(request: Request) -> EngineeringLabOptionsResponse:
    lab = request.app.state.container.engineering_lab_options
    return EngineeringLabOptionsResponse(
        sdk_enabled=lab.sdk_enabled,
        sdk_llm_review=lab.sdk_llm_review,
        sdk_llm_authorship=lab.sdk_llm_authorship,
        allow_unreviewed_sdk_play=lab.allow_unreviewed_sdk_play,
        preferred_play_runtime=lab.preferred_play_runtime,
    )


@router.patch(
    "/api/lab/engineering",
    response_model=EngineeringLabOptionsResponse,
    response_model_by_alias=True,
)
async def update_engineering_lab_options(
    body: EngineeringLabOptionsUpdateRequest, request: Request
) -> EngineeringLabOptionsResponse:
    lab = request.app.state.container.engineering_lab_options
    try:
        lab.apply(
            sdk_enabled=body.sdk_enabled,
            sdk_llm_review=body.sdk_llm_review,
            sdk_llm_authorship=body.sdk_llm_authorship,
            allow_unreviewed_sdk_play=body.allow_unreviewed_sdk_play,
            preferred_play_runtime=body.preferred_play_runtime,
        )
    except ValueError as exc:
        from fastapi import HTTPException

        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return EngineeringLabOptionsResponse(
        sdk_enabled=lab.sdk_enabled,
        sdk_llm_review=lab.sdk_llm_review,
        sdk_llm_authorship=lab.sdk_llm_authorship,
        allow_unreviewed_sdk_play=lab.allow_unreviewed_sdk_play,
        preferred_play_runtime=lab.preferred_play_runtime,
    )


@router.get("/", response_class=PlainTextResponse)
async def welcome() -> str:
    return "Welcome to Cyborg Studios API"

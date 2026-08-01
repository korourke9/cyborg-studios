from uuid import UUID

from fastapi import APIRouter, Request, status
from fastapi.responses import PlainTextResponse, Response

from gamebuilder.orchestration.application.usecase.get_project import ProjectDetails
from gamebuilder.orchestration.domain.model.project import Project
from gamebuilder.orchestration.interfaces.web.dtos import (
    ArtifactResponse,
    CreateProjectRequest,
    CreateProjectResponse,
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


@router.get("/", response_class=PlainTextResponse)
async def welcome() -> str:
    return "Welcome to Cyborg Studios API"

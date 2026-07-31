from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class CreateProjectRequest(BaseModel):
    prompt: str = Field(min_length=1)


class CreateProjectResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    project_id: UUID = Field(alias="projectId")
    status: str


class ArtifactResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: UUID
    type: str
    payload: str
    created_at: int = Field(alias="createdAt")


class ProjectResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: UUID
    prompt: str
    status: str
    created_at: int = Field(alias="createdAt")
    updated_at: int = Field(alias="updatedAt")
    artifacts: list[ArtifactResponse]

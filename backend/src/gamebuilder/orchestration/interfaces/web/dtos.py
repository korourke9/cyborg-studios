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


class ProjectSummaryResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: UUID
    prompt: str
    status: str
    created_at: int = Field(alias="createdAt")
    updated_at: int = Field(alias="updatedAt")


class ProjectResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: UUID
    prompt: str
    status: str
    created_at: int = Field(alias="createdAt")
    updated_at: int = Field(alias="updatedAt")
    artifacts: list[ArtifactResponse]


class PlayBundleInfoResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    project_id: UUID = Field(alias="projectId")
    title: str
    runtimes: list[str]
    sdk_review_verdict: str = Field(alias="sdkReviewVerdict")
    sdk_review_notes: list[str] = Field(alias="sdkReviewNotes")
    implemented: list[str]


# TEMP: remove before external release
class EngineeringLabOptionsResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    sdk_enabled: bool = Field(alias="sdkEnabled")
    sdk_llm_review: bool = Field(alias="sdkLlmReview")
    sdk_llm_authorship: bool = Field(alias="sdkLlmAuthorship")
    allow_unreviewed_sdk_play: bool = Field(alias="allowUnreviewedSdkPlay")
    preferred_play_runtime: str = Field(alias="preferredPlayRuntime")


class EngineeringLabOptionsUpdateRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    sdk_enabled: bool | None = Field(default=None, alias="sdkEnabled")
    sdk_llm_review: bool | None = Field(default=None, alias="sdkLlmReview")
    sdk_llm_authorship: bool | None = Field(default=None, alias="sdkLlmAuthorship")
    allow_unreviewed_sdk_play: bool | None = Field(
        default=None, alias="allowUnreviewedSdkPlay"
    )
    preferred_play_runtime: str | None = Field(
        default=None, alias="preferredPlayRuntime"
    )

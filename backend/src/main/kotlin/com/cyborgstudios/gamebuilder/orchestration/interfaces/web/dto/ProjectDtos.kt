package com.cyborgstudios.gamebuilder.orchestration.interfaces.web.dto

import com.cyborgstudios.gamebuilder.orchestration.domain.model.ArtifactType
import com.cyborgstudios.gamebuilder.orchestration.domain.model.ProjectStatus
import jakarta.validation.constraints.NotBlank
import java.util.UUID

data class CreateProjectRequest(
    @field:NotBlank
    val prompt: String
)

data class CreateProjectResponse(
    val projectId: UUID,
    val status: ProjectStatus
)

data class ArtifactResponse(
    val id: UUID,
    val type: ArtifactType,
    val payload: String,
    val createdAt: Long
)

data class ProjectResponse(
    val id: UUID,
    val prompt: String,
    val status: ProjectStatus,
    val createdAt: Long,
    val updatedAt: Long,
    val artifacts: List<ArtifactResponse>
)

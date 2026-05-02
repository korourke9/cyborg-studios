package com.cyborgstudios.gamebuilder.orchestration.interfaces.mappers

import com.cyborgstudios.gamebuilder.orchestration.application.usecase.ProjectDetails
import com.cyborgstudios.gamebuilder.orchestration.interfaces.web.dto.ArtifactResponse
import com.cyborgstudios.gamebuilder.orchestration.interfaces.web.dto.ProjectResponse
import org.springframework.stereotype.Component

@Component
class ProjectMapper {

    fun toProjectResponse(details: ProjectDetails): ProjectResponse = ProjectResponse(
        id = details.project.id,
        prompt = details.project.prompt,
        status = details.project.status,
        createdAt = details.project.createdAt,
        updatedAt = details.project.updatedAt,
        artifacts = details.artifacts.map { artifact ->
            ArtifactResponse(
                id = artifact.id,
                type = artifact.type,
                payload = artifact.payload,
                createdAt = artifact.createdAt
            )
        }
    )
}

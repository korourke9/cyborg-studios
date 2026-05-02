package com.cyborgstudios.gamebuilder.orchestration.application.usecase

import com.cyborgstudios.gamebuilder.orchestration.domain.model.Artifact
import com.cyborgstudios.gamebuilder.orchestration.domain.model.Project
import com.cyborgstudios.gamebuilder.orchestration.domain.repository.ArtifactRepository
import com.cyborgstudios.gamebuilder.orchestration.domain.repository.ProjectRepository
import java.util.UUID

class GetProjectUseCase(
    private val projectRepository: ProjectRepository,
    private val artifactRepository: ArtifactRepository
) {

    fun execute(projectId: UUID): ProjectDetails? {
        val project = projectRepository.findById(projectId) ?: return null
        val artifacts = artifactRepository.findByProjectId(projectId)
        return ProjectDetails(project = project, artifacts = artifacts)
    }
}

data class ProjectDetails(
    val project: Project,
    val artifacts: List<Artifact>
)

package com.cyborgstudios.gamebuilder.application.usecase

import com.cyborgstudios.gamebuilder.domain.model.Artifact
import com.cyborgstudios.gamebuilder.domain.model.Project
import com.cyborgstudios.gamebuilder.domain.repository.ArtifactRepository
import com.cyborgstudios.gamebuilder.domain.repository.ProjectRepository
import org.springframework.stereotype.Service
import java.util.UUID

@Service
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

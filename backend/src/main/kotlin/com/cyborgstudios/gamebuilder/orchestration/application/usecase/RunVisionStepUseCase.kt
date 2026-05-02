package com.cyborgstudios.gamebuilder.orchestration.application.usecase

import com.cyborgstudios.gamebuilder.orchestration.domain.model.ProjectStatus
import com.cyborgstudios.gamebuilder.orchestration.domain.repository.ArtifactRepository
import com.cyborgstudios.gamebuilder.orchestration.domain.repository.ProjectRepository
import com.cyborgstudios.gamebuilder.team.design.application.DesignersAgentService
import java.util.UUID

class RunVisionStepUseCase(
    private val projectRepository: ProjectRepository,
    private val artifactRepository: ArtifactRepository,
    private val designersAgentService: DesignersAgentService
) {

    fun execute(projectId: UUID) {
        val project = projectRepository.findById(projectId) ?: return

        projectRepository.updateStatus(projectId, ProjectStatus.VISION_IN_PROGRESS)

        val visionArtifact = designersAgentService.createVisionArtifact(projectId, project.prompt)
        artifactRepository.save(visionArtifact)

        projectRepository.updateStatus(projectId, ProjectStatus.VISION_DONE)
        projectRepository.updateStatus(projectId, ProjectStatus.DONE)
    }
}


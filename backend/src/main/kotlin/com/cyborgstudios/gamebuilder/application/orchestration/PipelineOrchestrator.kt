package com.cyborgstudios.gamebuilder.application.orchestration

import com.cyborgstudios.gamebuilder.application.team.design.DesignersAgentService
import com.cyborgstudios.gamebuilder.domain.model.ProjectStatus
import com.cyborgstudios.gamebuilder.domain.repository.ArtifactRepository
import com.cyborgstudios.gamebuilder.domain.repository.ProjectRepository
import org.springframework.scheduling.annotation.Async
import org.springframework.stereotype.Service
import java.util.UUID

@Service
class PipelineOrchestrator(
    private val projectRepository: ProjectRepository,
    private val artifactRepository: ArtifactRepository,
    private val designersAgentService: DesignersAgentService
) {

    @Async("pipelineExecutor")
    fun start(projectId: UUID) {
        val project = projectRepository.findById(projectId) ?: return

        try {
            projectRepository.updateStatus(projectId, ProjectStatus.VISION_IN_PROGRESS)

            val visionArtifact = designersAgentService.createVisionArtifact(projectId, project.prompt)
            artifactRepository.save(visionArtifact)

            projectRepository.updateStatus(projectId, ProjectStatus.VISION_DONE)
            projectRepository.updateStatus(projectId, ProjectStatus.DONE)
        } catch (_: Exception) {
            projectRepository.updateStatus(projectId, ProjectStatus.FAILED)
        }
    }
}

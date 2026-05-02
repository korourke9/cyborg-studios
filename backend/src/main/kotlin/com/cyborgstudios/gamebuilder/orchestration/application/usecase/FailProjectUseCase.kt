package com.cyborgstudios.gamebuilder.orchestration.application.usecase

import com.cyborgstudios.gamebuilder.orchestration.domain.model.ProjectStatus
import com.cyborgstudios.gamebuilder.orchestration.domain.repository.ProjectRepository
import java.util.UUID

class FailProjectUseCase(
    private val projectRepository: ProjectRepository
) {

    fun execute(projectId: UUID) {
        projectRepository.updateStatus(projectId, ProjectStatus.FAILED)
    }
}


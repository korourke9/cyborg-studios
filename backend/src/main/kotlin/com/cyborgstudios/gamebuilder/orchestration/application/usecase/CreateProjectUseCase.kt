package com.cyborgstudios.gamebuilder.orchestration.application.usecase

import com.cyborgstudios.gamebuilder.orchestration.domain.model.Project
import com.cyborgstudios.gamebuilder.orchestration.domain.model.ProjectStatus
import com.cyborgstudios.gamebuilder.orchestration.domain.repository.ProjectRepository
import java.util.UUID

class CreateProjectUseCase(
    private val projectRepository: ProjectRepository
) {

    fun execute(prompt: String): Project {
        val now = System.currentTimeMillis()
        val project = Project(
            id = UUID.randomUUID(),
            prompt = prompt,
            status = ProjectStatus.PENDING,
            createdAt = now,
            updatedAt = now
        )
        return projectRepository.save(project)
    }
}

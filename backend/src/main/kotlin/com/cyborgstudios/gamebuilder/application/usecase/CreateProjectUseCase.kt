package com.cyborgstudios.gamebuilder.application.usecase

import com.cyborgstudios.gamebuilder.domain.model.Project
import com.cyborgstudios.gamebuilder.domain.model.ProjectStatus
import com.cyborgstudios.gamebuilder.domain.repository.ProjectRepository
import org.springframework.stereotype.Service
import java.util.UUID

@Service
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

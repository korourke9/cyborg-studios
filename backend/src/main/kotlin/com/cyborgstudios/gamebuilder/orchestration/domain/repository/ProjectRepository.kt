package com.cyborgstudios.gamebuilder.orchestration.domain.repository

import com.cyborgstudios.gamebuilder.orchestration.domain.model.Project
import com.cyborgstudios.gamebuilder.orchestration.domain.model.ProjectStatus
import java.util.UUID

interface ProjectRepository {

    fun save(project: Project): Project

    fun findById(id: UUID): Project?

    fun updateStatus(id: UUID, status: ProjectStatus): Boolean
}

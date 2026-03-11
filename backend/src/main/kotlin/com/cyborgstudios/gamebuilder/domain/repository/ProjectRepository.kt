package com.cyborgstudios.gamebuilder.domain.repository

import com.cyborgstudios.gamebuilder.domain.model.Project
import com.cyborgstudios.gamebuilder.domain.model.ProjectStatus
import java.util.UUID

interface ProjectRepository {

    fun save(project: Project): Project

    fun findById(id: UUID): Project?

    fun updateStatus(id: UUID, status: ProjectStatus): Boolean
}

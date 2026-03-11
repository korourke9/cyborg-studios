package com.cyborgstudios.gamebuilder.infrastructure.persistence

import com.cyborgstudios.gamebuilder.domain.model.Project
import com.cyborgstudios.gamebuilder.domain.model.ProjectStatus
import com.cyborgstudios.gamebuilder.domain.repository.ProjectRepository
import org.jetbrains.exposed.v1.core.and
import org.jetbrains.exposed.v1.core.eq
import org.jetbrains.exposed.v1.jdbc.insert
import org.jetbrains.exposed.v1.jdbc.selectAll
import org.jetbrains.exposed.v1.jdbc.transactions.transaction
import org.jetbrains.exposed.v1.jdbc.update
import org.springframework.stereotype.Repository

import java.util.UUID

@Repository
class ExposedProjectRepository : ProjectRepository {

    override fun save(project: Project): Project = transaction {
        ProjectsTable.insert {
            it[ProjectsTable.id] = project.id.toString()
            it[ProjectsTable.prompt] = project.prompt
            it[ProjectsTable.status] = project.status.name
            it[ProjectsTable.createdAt] = project.createdAt
            it[ProjectsTable.updatedAt] = project.updatedAt
        }
        project
    }

    override fun findById(id: UUID): Project? = transaction {
        ProjectsTable.selectAll().where { ProjectsTable.id eq id.toString() }
            .singleOrNull()
            ?.let { row ->
                Project(
                    id = UUID.fromString(row[ProjectsTable.id]),
                    prompt = row[ProjectsTable.prompt],
                    status = ProjectStatus.valueOf(row[ProjectsTable.status]),
                    createdAt = row[ProjectsTable.createdAt],
                    updatedAt = row[ProjectsTable.updatedAt]
                )
            }
    }

    override fun updateStatus(id: UUID, status: ProjectStatus): Boolean = transaction {
        val updatedAt = System.currentTimeMillis()
        ProjectsTable.update({ ProjectsTable.id eq id.toString() }) {
            it[ProjectsTable.status] = status.name
            it[ProjectsTable.updatedAt] = updatedAt
        } > 0
    }
}

package com.cyborgstudios.gamebuilder.orchestration.infrastructure.persistence

import com.cyborgstudios.gamebuilder.orchestration.domain.model.Artifact
import com.cyborgstudios.gamebuilder.orchestration.domain.model.ArtifactType
import com.cyborgstudios.gamebuilder.orchestration.domain.repository.ArtifactRepository
import org.jetbrains.exposed.v1.core.and
import org.jetbrains.exposed.v1.core.eq
import org.jetbrains.exposed.v1.jdbc.insert
import org.jetbrains.exposed.v1.jdbc.selectAll
import org.jetbrains.exposed.v1.jdbc.transactions.transaction
import org.jetbrains.exposed.v1.jdbc.update
import org.springframework.stereotype.Repository
import java.util.UUID

@Repository
class ExposedArtifactRepository : ArtifactRepository {

    override fun save(artifact: Artifact): Artifact = transaction {
        ArtifactsTable.insert {
            it[ArtifactsTable.id] = artifact.id.toString()
            it[ArtifactsTable.projectId] = artifact.projectId.toString()
            it[ArtifactsTable.type] = artifact.type.name
            it[ArtifactsTable.payload] = artifact.payload
            it[ArtifactsTable.createdAt] = artifact.createdAt
        }
        artifact
    }

    override fun findById(id: UUID): Artifact? = transaction {
        ArtifactsTable.selectAll().where { ArtifactsTable.id eq id.toString() }
            .singleOrNull()
            ?.let { row ->
                Artifact(
                    id = UUID.fromString(row[ArtifactsTable.id]),
                    projectId = UUID.fromString(row[ArtifactsTable.projectId]),
                    type = ArtifactType.valueOf(row[ArtifactsTable.type]),
                    payload = row[ArtifactsTable.payload],
                    createdAt = row[ArtifactsTable.createdAt]
                )
            }
    }

    override fun findByProjectId(projectId: UUID): List<Artifact> = transaction {
        ArtifactsTable.selectAll().where { ArtifactsTable.projectId eq projectId.toString() }
            .map { row ->
                Artifact(
                    id = UUID.fromString(row[ArtifactsTable.id]),
                    projectId = UUID.fromString(row[ArtifactsTable.projectId]),
                    type = ArtifactType.valueOf(row[ArtifactsTable.type]),
                    payload = row[ArtifactsTable.payload],
                    createdAt = row[ArtifactsTable.createdAt]
                )
            }
    }

    override fun findByProjectIdAndType(projectId: UUID, type: ArtifactType): Artifact? = transaction {
        ArtifactsTable.selectAll().where {
            (ArtifactsTable.projectId eq projectId.toString()) and (ArtifactsTable.type eq type.name)
        }
            .singleOrNull()
            ?.let { row ->
                Artifact(
                    id = UUID.fromString(row[ArtifactsTable.id]),
                    projectId = UUID.fromString(row[ArtifactsTable.projectId]),
                    type = ArtifactType.valueOf(row[ArtifactsTable.type]),
                    payload = row[ArtifactsTable.payload],
                    createdAt = row[ArtifactsTable.createdAt]
                )
            }
    }
}

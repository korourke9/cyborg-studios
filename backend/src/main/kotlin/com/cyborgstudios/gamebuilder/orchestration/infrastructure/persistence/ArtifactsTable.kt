package com.cyborgstudios.gamebuilder.orchestration.infrastructure.persistence

import org.jetbrains.exposed.v1.core.Table

object ArtifactsTable : Table("artifacts") {
    val id = varchar("id", 36)
    val projectId = varchar("project_id", 36)
    val type = varchar("type", 50)
    val payload = text("payload")
    val createdAt = long("created_at")

    override val primaryKey = PrimaryKey(id)
}

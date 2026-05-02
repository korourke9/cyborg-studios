package com.cyborgstudios.gamebuilder.orchestration.infrastructure.persistence

import org.jetbrains.exposed.v1.core.Table

object ProjectsTable : Table("projects") {
    val id = varchar("id", 36)
    val prompt = text("prompt")
    val status = varchar("status", 50)
    val createdAt = long("created_at")
    val updatedAt = long("updated_at")

    override val primaryKey = PrimaryKey(id)
}

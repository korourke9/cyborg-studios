package com.cyborgstudios.gamebuilder.orchestration.domain.model

import java.util.UUID

data class Project(
    val id: UUID,
    val prompt: String,
    val status: ProjectStatus,
    val createdAt: Long,
    val updatedAt: Long
)

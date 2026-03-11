package com.cyborgstudios.gamebuilder.domain.model

import java.util.UUID

data class Artifact(
    val id: UUID,
    val projectId: UUID,
    val type: ArtifactType,
    val payload: String,
    val createdAt: Long
)

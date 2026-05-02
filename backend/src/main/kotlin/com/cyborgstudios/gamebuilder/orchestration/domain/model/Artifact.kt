package com.cyborgstudios.gamebuilder.orchestration.domain.model

import java.util.UUID

data class Artifact(
    val id: UUID,
    val projectId: UUID,
    val type: ArtifactType,
    val payload: String,
    val createdAt: Long
)

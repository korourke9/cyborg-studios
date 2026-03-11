package com.cyborgstudios.gamebuilder.domain.repository

import com.cyborgstudios.gamebuilder.domain.model.Artifact
import com.cyborgstudios.gamebuilder.domain.model.ArtifactType
import java.util.UUID

interface ArtifactRepository {

    fun save(artifact: Artifact): Artifact

    fun findById(id: UUID): Artifact?

    fun findByProjectId(projectId: UUID): List<Artifact>

    fun findByProjectIdAndType(projectId: UUID, type: ArtifactType): Artifact?
}

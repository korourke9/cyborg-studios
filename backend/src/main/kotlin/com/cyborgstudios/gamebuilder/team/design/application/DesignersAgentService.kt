package com.cyborgstudios.gamebuilder.team.design.application

import com.cyborgstudios.gamebuilder.orchestration.domain.model.Artifact
import com.cyborgstudios.gamebuilder.orchestration.domain.model.ArtifactType
import java.util.UUID

class DesignersAgentService {

    fun createVisionArtifact(projectId: UUID, prompt: String): Artifact {
        val payload = """
            {"summary":"Vision generated for prompt: ${escapeJson(prompt)}"}
        """.trimIndent()

        return Artifact(
            id = UUID.randomUUID(),
            projectId = projectId,
            type = ArtifactType.VISION_DOC,
            payload = payload,
            createdAt = System.currentTimeMillis()
        )
    }

    private fun escapeJson(input: String): String =
        input.replace("\\", "\\\\").replace("\"", "\\\"")
}

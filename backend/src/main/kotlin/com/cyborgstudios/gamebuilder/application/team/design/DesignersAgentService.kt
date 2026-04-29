package com.cyborgstudios.gamebuilder.application.team.design

import com.cyborgstudios.gamebuilder.domain.model.Artifact
import com.cyborgstudios.gamebuilder.domain.model.ArtifactType
import org.springframework.stereotype.Service
import java.util.UUID

@Service
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

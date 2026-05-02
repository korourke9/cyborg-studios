package com.cyborgstudios.gamebuilder.orchestration.application.usecase

import com.cyborgstudios.gamebuilder.orchestration.application.port.GenerationWorkflowRunner
import java.util.UUID

class StartProjectGenerationUseCase(
    private val generationWorkflowRunner: GenerationWorkflowRunner
) {

    fun execute(projectId: UUID) {
        generationWorkflowRunner.start(projectId)
    }
}


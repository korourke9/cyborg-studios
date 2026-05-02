package com.cyborgstudios.gamebuilder.orchestration.application.port

import java.util.UUID

interface GenerationWorkflowRunner {

    fun start(projectId: UUID)
}


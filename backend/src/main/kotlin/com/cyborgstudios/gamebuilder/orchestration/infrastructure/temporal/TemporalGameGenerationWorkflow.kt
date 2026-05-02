package com.cyborgstudios.gamebuilder.orchestration.infrastructure.temporal

import io.temporal.workflow.WorkflowInterface
import io.temporal.workflow.WorkflowMethod

@WorkflowInterface
interface TemporalGameGenerationWorkflow {

    @WorkflowMethod
    fun run(projectId: String)
}


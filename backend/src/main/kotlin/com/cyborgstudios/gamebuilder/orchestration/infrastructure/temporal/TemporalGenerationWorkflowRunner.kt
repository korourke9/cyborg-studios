package com.cyborgstudios.gamebuilder.orchestration.infrastructure.temporal

import com.cyborgstudios.gamebuilder.orchestration.application.port.GenerationWorkflowRunner
import io.temporal.client.WorkflowClient
import io.temporal.client.WorkflowOptions
import java.util.UUID

class TemporalGenerationWorkflowRunner(
    private val workflowClient: WorkflowClient,
    private val taskQueue: String
) : GenerationWorkflowRunner {

    override fun start(projectId: UUID) {
        val workflow = workflowClient.newWorkflowStub(
            TemporalGameGenerationWorkflow::class.java,
            WorkflowOptions.newBuilder()
                .setTaskQueue(taskQueue)
                .setWorkflowId("game-generation-$projectId")
                .build()
        )

        WorkflowClient.start(workflow::run, projectId.toString())
    }
}


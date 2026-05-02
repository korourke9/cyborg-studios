package com.cyborgstudios.gamebuilder.orchestration.infrastructure.temporal

import io.temporal.activity.ActivityOptions
import io.temporal.common.RetryOptions
import io.temporal.workflow.Workflow
import java.time.Duration

class TemporalGameGenerationWorkflowImpl : TemporalGameGenerationWorkflow {

    private val activities = Workflow.newActivityStub(
        TemporalGameGenerationActivities::class.java,
        ActivityOptions.newBuilder()
            .setStartToCloseTimeout(Duration.ofMinutes(5))
            .setRetryOptions(
                RetryOptions.newBuilder()
                    .setMaximumAttempts(3)
                    .build()
            )
            .build()
    )

    override fun run(projectId: String) {
        try {
            activities.runVisionStep(projectId)
        } catch (e: Exception) {
            activities.failProject(projectId)
            throw e
        }
    }
}


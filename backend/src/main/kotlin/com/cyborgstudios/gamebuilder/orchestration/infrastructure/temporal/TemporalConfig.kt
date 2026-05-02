package com.cyborgstudios.gamebuilder.orchestration.infrastructure.temporal

import com.cyborgstudios.gamebuilder.orchestration.application.port.GenerationWorkflowRunner
import com.cyborgstudios.gamebuilder.orchestration.application.usecase.FailProjectUseCase
import com.cyborgstudios.gamebuilder.orchestration.application.usecase.RunVisionStepUseCase
import io.temporal.client.WorkflowClient
import io.temporal.client.WorkflowClientOptions
import io.temporal.serviceclient.WorkflowServiceStubs
import io.temporal.serviceclient.WorkflowServiceStubsOptions
import io.temporal.worker.Worker
import io.temporal.worker.WorkerFactory
import org.springframework.beans.factory.annotation.Value
import org.springframework.boot.autoconfigure.condition.ConditionalOnMissingBean
import org.springframework.boot.context.event.ApplicationReadyEvent
import org.springframework.context.ApplicationListener
import org.springframework.context.annotation.Bean
import org.springframework.context.annotation.Configuration

@Configuration
class TemporalConfig(
    @param:Value("\${app.temporal.target}") private val target: String,
    @param:Value("\${app.temporal.namespace}") private val namespace: String,
    @param:Value("\${app.temporal.task-queue}") private val taskQueue: String
) {

    @Bean
    @ConditionalOnMissingBean
    fun workflowServiceStubs(): WorkflowServiceStubs =
        WorkflowServiceStubs.newServiceStubs(
            WorkflowServiceStubsOptions.newBuilder()
                .setTarget(target)
                .build()
        )

    @Bean
    @ConditionalOnMissingBean
    fun workflowClient(workflowServiceStubs: WorkflowServiceStubs): WorkflowClient =
        WorkflowClient.newInstance(
            workflowServiceStubs,
            WorkflowClientOptions.newBuilder()
                .setNamespace(namespace)
                .build()
        )

    @Bean
    fun workerFactory(workflowClient: WorkflowClient): WorkerFactory =
        WorkerFactory.newInstance(workflowClient)

    @Bean
    fun generationWorkflowRunner(workflowClient: WorkflowClient): GenerationWorkflowRunner =
        TemporalGenerationWorkflowRunner(workflowClient, taskQueue)

    @Bean
    fun gameGenerationActivities(
        runVisionStepUseCase: RunVisionStepUseCase,
        failProjectUseCase: FailProjectUseCase
    ): TemporalGameGenerationActivities =
        TemporalGameGenerationActivitiesImpl(runVisionStepUseCase, failProjectUseCase)

    @Bean
    fun gameGenerationWorker(
        workerFactory: WorkerFactory,
        activities: TemporalGameGenerationActivities
    ): Worker {
        val worker = workerFactory.newWorker(taskQueue)
        worker.registerWorkflowImplementationTypes(TemporalGameGenerationWorkflowImpl::class.java)
        worker.registerActivitiesImplementations(activities)
        return worker
    }

    @Bean
    fun temporalWorkerStarter(workerFactory: WorkerFactory): ApplicationListener<ApplicationReadyEvent> =
        ApplicationListener {
            workerFactory.start()
        }
}


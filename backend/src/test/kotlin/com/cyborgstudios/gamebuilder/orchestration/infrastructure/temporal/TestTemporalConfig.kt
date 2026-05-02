package com.cyborgstudios.gamebuilder.orchestration.infrastructure.temporal

import io.temporal.client.WorkflowClient
import io.temporal.serviceclient.WorkflowServiceStubs
import io.temporal.testing.TestWorkflowEnvironment
import org.springframework.context.annotation.Bean
import org.springframework.context.annotation.Configuration
import org.springframework.context.annotation.Profile

@Configuration
@Profile("test")
class TestTemporalConfig {

    @Bean(destroyMethod = "close")
    fun testWorkflowEnvironment(): TestWorkflowEnvironment =
        TestWorkflowEnvironment.newInstance()

    @Bean
    fun workflowServiceStubs(testWorkflowEnvironment: TestWorkflowEnvironment): WorkflowServiceStubs =
        testWorkflowEnvironment.workflowServiceStubs

    @Bean
    fun workflowClient(testWorkflowEnvironment: TestWorkflowEnvironment): WorkflowClient =
        testWorkflowEnvironment.workflowClient
}


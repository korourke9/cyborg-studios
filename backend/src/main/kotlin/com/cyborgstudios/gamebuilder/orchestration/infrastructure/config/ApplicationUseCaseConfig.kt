package com.cyborgstudios.gamebuilder.orchestration.infrastructure.config

import com.cyborgstudios.gamebuilder.orchestration.application.port.GenerationWorkflowRunner
import com.cyborgstudios.gamebuilder.orchestration.application.usecase.CreateProjectUseCase
import com.cyborgstudios.gamebuilder.orchestration.application.usecase.FailProjectUseCase
import com.cyborgstudios.gamebuilder.orchestration.application.usecase.GetProjectUseCase
import com.cyborgstudios.gamebuilder.orchestration.application.usecase.RunVisionStepUseCase
import com.cyborgstudios.gamebuilder.orchestration.application.usecase.StartProjectGenerationUseCase
import com.cyborgstudios.gamebuilder.orchestration.domain.repository.ArtifactRepository
import com.cyborgstudios.gamebuilder.orchestration.domain.repository.ProjectRepository
import com.cyborgstudios.gamebuilder.team.design.application.DesignersAgentService
import org.springframework.context.annotation.Bean
import org.springframework.context.annotation.Configuration

@Configuration
class ApplicationUseCaseConfig {

    @Bean
    fun createProjectUseCase(projectRepository: ProjectRepository): CreateProjectUseCase =
        CreateProjectUseCase(projectRepository)

    @Bean
    fun getProjectUseCase(
        projectRepository: ProjectRepository,
        artifactRepository: ArtifactRepository
    ): GetProjectUseCase =
        GetProjectUseCase(projectRepository, artifactRepository)

    @Bean
    fun startProjectGenerationUseCase(generationWorkflowRunner: GenerationWorkflowRunner): StartProjectGenerationUseCase =
        StartProjectGenerationUseCase(generationWorkflowRunner)

    @Bean
    fun runVisionStepUseCase(
        projectRepository: ProjectRepository,
        artifactRepository: ArtifactRepository,
        designersAgentService: DesignersAgentService
    ): RunVisionStepUseCase =
        RunVisionStepUseCase(projectRepository, artifactRepository, designersAgentService)

    @Bean
    fun failProjectUseCase(projectRepository: ProjectRepository): FailProjectUseCase =
        FailProjectUseCase(projectRepository)

    @Bean
    fun designersAgentService(): DesignersAgentService =
        DesignersAgentService()
}


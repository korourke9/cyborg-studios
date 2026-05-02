package com.cyborgstudios.gamebuilder.orchestration.infrastructure.temporal

import com.cyborgstudios.gamebuilder.orchestration.application.usecase.FailProjectUseCase
import com.cyborgstudios.gamebuilder.orchestration.application.usecase.RunVisionStepUseCase
import java.util.UUID

class TemporalGameGenerationActivitiesImpl(
    private val runVisionStepUseCase: RunVisionStepUseCase,
    private val failProjectUseCase: FailProjectUseCase
) : TemporalGameGenerationActivities {

    override fun runVisionStep(projectId: String) {
        runVisionStepUseCase.execute(UUID.fromString(projectId))
    }

    override fun failProject(projectId: String) {
        failProjectUseCase.execute(UUID.fromString(projectId))
    }
}


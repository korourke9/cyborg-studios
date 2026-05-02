package com.cyborgstudios.gamebuilder.orchestration.infrastructure.temporal

import io.temporal.activity.ActivityInterface
import io.temporal.activity.ActivityMethod

@ActivityInterface
interface TemporalGameGenerationActivities {

    @ActivityMethod
    fun runVisionStep(projectId: String)

    @ActivityMethod
    fun failProject(projectId: String)
}


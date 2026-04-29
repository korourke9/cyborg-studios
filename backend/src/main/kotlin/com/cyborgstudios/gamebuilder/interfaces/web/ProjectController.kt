package com.cyborgstudios.gamebuilder.interfaces.web

import com.cyborgstudios.gamebuilder.application.orchestration.PipelineOrchestrator
import com.cyborgstudios.gamebuilder.application.usecase.CreateProjectUseCase
import com.cyborgstudios.gamebuilder.application.usecase.GetProjectUseCase
import com.cyborgstudios.gamebuilder.interfaces.mappers.ProjectMapper
import com.cyborgstudios.gamebuilder.interfaces.web.dto.CreateProjectRequest
import com.cyborgstudios.gamebuilder.interfaces.web.dto.CreateProjectResponse
import com.cyborgstudios.gamebuilder.interfaces.web.dto.ProjectResponse
import jakarta.validation.Valid
import org.springframework.http.HttpStatus
import org.springframework.http.ResponseEntity
import org.springframework.web.bind.annotation.GetMapping
import org.springframework.web.bind.annotation.PathVariable
import org.springframework.web.bind.annotation.PostMapping
import org.springframework.web.bind.annotation.RequestBody
import org.springframework.web.bind.annotation.RequestMapping
import org.springframework.web.bind.annotation.RestController
import java.util.UUID

@RestController
@RequestMapping("/api/projects")
class ProjectController(
    private val createProjectUseCase: CreateProjectUseCase,
    private val getProjectUseCase: GetProjectUseCase,
    private val pipelineOrchestrator: PipelineOrchestrator,
    private val projectMapper: ProjectMapper
) {

    @PostMapping
    fun createProject(@Valid @RequestBody request: CreateProjectRequest): ResponseEntity<CreateProjectResponse> {
        val project = createProjectUseCase.execute(request.prompt)
        pipelineOrchestrator.start(project.id)

        return ResponseEntity.status(HttpStatus.ACCEPTED)
            .body(CreateProjectResponse(projectId = project.id, status = project.status))
    }

    @GetMapping("/{projectId}")
    fun getProject(@PathVariable projectId: UUID): ResponseEntity<ProjectResponse> {
        val details = getProjectUseCase.execute(projectId) ?: return ResponseEntity.notFound().build()
        return ResponseEntity.ok(projectMapper.toProjectResponse(details))
    }
}

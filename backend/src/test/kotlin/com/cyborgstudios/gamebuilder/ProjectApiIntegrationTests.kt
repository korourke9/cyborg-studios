package com.cyborgstudios.gamebuilder

import com.cyborgstudios.gamebuilder.interfaces.web.dto.CreateProjectRequest
import com.cyborgstudios.gamebuilder.interfaces.web.dto.CreateProjectResponse
import com.cyborgstudios.gamebuilder.interfaces.web.dto.ProjectResponse
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertNotNull
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test
import org.springframework.beans.factory.annotation.Autowired
import org.springframework.boot.test.context.SpringBootTest
import org.springframework.boot.test.web.client.TestRestTemplate
import org.springframework.http.HttpEntity
import org.springframework.http.HttpMethod
import org.springframework.http.HttpStatus
import org.springframework.test.context.ActiveProfiles
import java.util.UUID

@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
@ActiveProfiles("test")
class ProjectApiIntegrationTests {

    @Autowired
    lateinit var restTemplate: TestRestTemplate

    @Test
    fun createThenPollProjectUntilDone() {
        val createResponse = restTemplate.postForEntity(
            "/api/projects",
            CreateProjectRequest(prompt = "A tiny robot adventure"),
            CreateProjectResponse::class.java
        )

        assertEquals(HttpStatus.ACCEPTED, createResponse.statusCode)
        val projectId = createResponse.body?.projectId
        assertNotNull(projectId)

        val doneProject = waitForProjectDone(projectId!!)
        assertEquals("A tiny robot adventure", doneProject.prompt)
        assertEquals("DONE", doneProject.status.name)
        assertTrue(doneProject.artifacts.any { it.type.name == "VISION_DOC" })
    }

    @Test
    fun getUnknownProjectReturnsNotFound() {
        val response = restTemplate.getForEntity(
            "/api/projects/${UUID.randomUUID()}",
            ProjectResponse::class.java
        )

        assertEquals(HttpStatus.NOT_FOUND, response.statusCode)
    }

    private fun waitForProjectDone(projectId: UUID): ProjectResponse {
        repeat(20) {
            val response = restTemplate.exchange(
                "/api/projects/$projectId",
                HttpMethod.GET,
                HttpEntity.EMPTY,
                ProjectResponse::class.java
            )

            if (response.statusCode == HttpStatus.OK && response.body?.status?.name == "DONE") {
                return response.body!!
            }

            Thread.sleep(150)
        }

        error("Project did not reach DONE status in time")
    }
}

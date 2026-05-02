package com.cyborgstudios.gamebuilder

import org.junit.jupiter.api.Test
import org.springframework.boot.test.context.SpringBootTest
import org.springframework.test.context.ActiveProfiles

@SpringBootTest
@ActiveProfiles("test")
class GameBuilderApplicationTests {

    @Test
    fun contextLoads() {
        // Verifies that the Spring context can start with the current configuration
    }
}


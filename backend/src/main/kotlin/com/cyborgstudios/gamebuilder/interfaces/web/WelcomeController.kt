package com.cyborgstudios.gamebuilder.interfaces.web

import org.springframework.web.bind.annotation.GetMapping
import org.springframework.web.bind.annotation.RestController

@RestController
class WelcomeController {

    @GetMapping("/")
    fun welcome(): String = "Welcome to Cyborg Studios API"
}


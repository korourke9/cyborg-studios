package com.cyborgstudios.gamebuilder

import org.springframework.boot.autoconfigure.SpringBootApplication
import org.springframework.boot.runApplication

@SpringBootApplication
class GameBuilderApplication

fun main(args: Array<String>) {
    runApplication<GameBuilderApplication>(*args)
}


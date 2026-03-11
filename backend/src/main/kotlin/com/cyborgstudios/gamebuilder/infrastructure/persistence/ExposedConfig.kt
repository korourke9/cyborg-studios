package com.cyborgstudios.gamebuilder.infrastructure.persistence

import org.jetbrains.exposed.v1.jdbc.Database
import org.jetbrains.exposed.v1.jdbc.SchemaUtils
import org.jetbrains.exposed.v1.jdbc.transactions.transaction
import org.springframework.context.annotation.Bean
import org.springframework.context.annotation.Configuration
import javax.sql.DataSource

@Configuration
class ExposedConfig {

    @Bean
    fun exposedDatabase(dataSource: DataSource): Database {
        val database = Database.connect(dataSource)
        transaction(database) {
            SchemaUtils.createMissingTablesAndColumns(ProjectsTable, ArtifactsTable)
        }
        return database
    }
}

# Create schema
CREATE SCHEMA IF NOT EXISTS `seddb` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;


USE seddb;


# Create users TABLE
CREATE TABLE IF NOT EXISTS `seddb`.`users`
(
    `id`        INT UNSIGNED     NOT NULL AUTO_INCREMENT,
    `username`  VARCHAR(45)      NOT NULL,
    `password`  VARCHAR(100)     NOT NULL,
    `email`     VARCHAR(100)     NULL,
    `full_name` VARCHAR(255)     NULL,
    `scopes`    VARCHAR(500)     NULL     DEFAULT '',
    `disabled`  TINYINT UNSIGNED NOT NULL DEFAULT 0,
    PRIMARY KEY (`id`),
    UNIQUE INDEX `id_UNIQUE` (`id` ASC) VISIBLE,
    UNIQUE INDEX `username_UNIQUE` (`username` ASC) VISIBLE
);


# Create projects table
CREATE TABLE IF NOT EXISTS `seddb`.`projects`
(
    `id`   INT UNSIGNED NOT NULL AUTO_INCREMENT,
    `name` VARCHAR(255) NOT NULL,
    PRIMARY KEY (`id`),
    UNIQUE INDEX `id_UNIQUE` (`id` ASC) VISIBLE
);


CREATE TABLE IF NOT EXISTS `seddb`.`projects_participants`
(
    `id`           INT UNSIGNED NOT NULL AUTO_INCREMENT,
    `user_id`      INT UNSIGNED NOT NULL,
    `project_id`   INT UNSIGNED NOT NULL,
    `access_level` INT UNSIGNED NOT NULL,
    PRIMARY KEY (`id`),
    UNIQUE INDEX `id_UNIQUE` (`id` ASC) VISIBLE,
    CONSTRAINT `project_cascade`
        FOREIGN KEY (`project_id`)
            REFERENCES `seddb`.`projects` (`id`)
            ON DELETE CASCADE
            ON UPDATE NO ACTION,
    INDEX `user_cascade_idx` (`user_id` ASC) VISIBLE,
    CONSTRAINT `user_cascade`
        FOREIGN KEY (`user_id`)
            REFERENCES `seddb`.`users` (`id`)
            ON DELETE CASCADE
            ON UPDATE NO ACTION
);


CREATE TABLE IF NOT EXISTS `seddb`.`projects_subprojects`
(
    `id`                INT UNSIGNED NOT NULL AUTO_INCREMENT,
    `application_sid`   VARCHAR(255) NOT NULL,
    `project_id`        INT UNSIGNED NULL DEFAULT NULL,
    `native_project_id` INT UNSIGNED NOT NULL,
    `owner_id`          INT UNSIGNED NOT NULL,
    PRIMARY KEY (`id`),
    INDEX `NATIVE_SUBPROJ_ID` (`native_project_id` ASC) INVISIBLE,
    INDEX `projects_cascade_idx` (`project_id` ASC) VISIBLE,
    CONSTRAINT `projects_cascade`
        FOREIGN KEY (`project_id`)
            REFERENCES `seddb`.`projects` (`id`)
            ON DELETE CASCADE
);


# Create individuals table
CREATE TABLE IF NOT EXISTS `seddb`.`individuals`
(
    `id`           INT UNSIGNED     NOT NULL AUTO_INCREMENT,
    `name`         VARCHAR(255)     NOT NULL DEFAULT 'Unnamed individuals',
    `is_archetype` TINYINT UNSIGNED NOT NULL DEFAULT 0,
    PRIMARY KEY (`id`),
    UNIQUE INDEX `id_UNIQUE` (`id` ASC) VISIBLE
);


# Create parameter table
CREATE TABLE IF NOT EXISTS `seddb`.`individuals_parameters`
(
    `id`            INT UNSIGNED     NOT NULL AUTO_INCREMENT,
    `name`          VARCHAR(255)     NOT NULL,
    `value`         VARCHAR(255)     NULL DEFAULT NULL,
    `type`          TINYINT UNSIGNED NOT NULL,
    `individual_id` INT UNSIGNED     NOT NULL,
    PRIMARY KEY (`id`),
    UNIQUE INDEX `id_UNIQUE` (`id` ASC) VISIBLE,
    INDEX `individuals_cascade_idx` (`individual_id` ASC) VISIBLE,
    CONSTRAINT `individuals_cascade`
        FOREIGN KEY (`individual_id`)
            REFERENCES `seddb`.`individuals` (`id`)
            ON DELETE CASCADE
            ON UPDATE NO ACTION
);


# Create individual to archetypes map
CREATE TABLE IF NOT EXISTS `seddb`.`individuals_archetypes_map`
(
    `id`                      INT UNSIGNED NOT NULL AUTO_INCREMENT,
    `individual_archetype_id` INT UNSIGNED NOT NULL,
    `individual_id`           INT UNSIGNED NOT NULL,
    PRIMARY KEY (`id`),
    UNIQUE INDEX `id_UNIQUE` (`id` ASC) VISIBLE,
    INDEX `individual_cascade_idx` (`individual_id` ASC) VISIBLE,
    CONSTRAINT `individual_cascade`
        FOREIGN KEY (`individual_id`)
            REFERENCES `seddb`.`individuals` (`id`)
            ON DELETE CASCADE
            ON UPDATE NO ACTION
);


CREATE TABLE IF NOT EXISTS `seddb`.`measurements_sets`
(
    `id`          INT UNSIGNED     NOT NULL AUTO_INCREMENT,
    `name`        VARCHAR(255)     NOT NULL DEFAULT 'Unnamed measurement set',
    `type`        TINYINT UNSIGNED NOT NULL DEFAULT 0,
    `description` TEXT             NULL,
    PRIMARY KEY (`id`),
    UNIQUE INDEX `id_UNIQUE` (`id` ASC) VISIBLE
);


# Measurements table
CREATE TABLE IF NOT EXISTS `seddb`.`measurements`
(
    `id`                 INT UNSIGNED     NOT NULL AUTO_INCREMENT,
    `name`               VARCHAR(255)     NOT NULL DEFAULT 'Unnamed measurement',
    `type`               TINYINT UNSIGNED NOT NULL,
    `description`        TEXT             NULL,
    `measurement_set_id` INT UNSIGNED     NOT NULL,
    PRIMARY KEY (`id`),
    INDEX `measurement_set_cascade_idx` (`measurement_set_id` ASC) VISIBLE,
    CONSTRAINT `measurement_set_cascade`
        FOREIGN KEY (`measurement_set_id`)
            REFERENCES `seddb`.`measurements_sets` (`id`)
            ON DELETE CASCADE
            ON UPDATE NO ACTION
);


# Measurement data table
CREATE TABLE IF NOT EXISTS `seddb`.`measurements_results_data`
(
    `id`                    INT UNSIGNED     NOT NULL AUTO_INCREMENT,
    `measurement_id`        INT UNSIGNED     NOT NULL,
    `individual_id`         INT UNSIGNED,
    `value`                 VARCHAR(255)     NOT NULL,
    `type`                  TINYINT UNSIGNED NOT NULL,
    `insert_timestamp`      DATETIME(3)      NOT NULL DEFAULT NOW(3),
    `measurement_timestamp` DATETIME(3)      NULL     DEFAULT NULL,
    PRIMARY KEY (`id`),
    UNIQUE INDEX `id_UNIQUE` (`id` ASC) VISIBLE,
    INDEX `measurement_data_measurements_cascade_idx` (`measurement_id` ASC) VISIBLE,
    CONSTRAINT `measurement_data_measurements_cascade`
        FOREIGN KEY (`measurement_id`)
            REFERENCES `seddb`.`measurements` (`id`)
            ON DELETE CASCADE
            ON UPDATE NO ACTION
);


# Measurements result files table
CREATE TABLE IF NOT EXISTS `seddb`.`measurements_results_files`
(
    `id`               INT UNSIGNED NOT NULL AUTO_INCREMENT,
    `measurement_id`   INT UNSIGNED NOT NULL,
    `individual_id`    INT UNSIGNED,
    `file`             VARCHAR(500) NOT NULL,
    `insert_timestamp` DATETIME(3)  NOT NULL DEFAULT NOW(3),
    PRIMARY KEY (`id`),
    UNIQUE INDEX `id_UNIQUE` (`id` ASC) VISIBLE,
    UNIQUE INDEX `measurement_id_UNIQUE` (`measurement_id` ASC) VISIBLE,
    CONSTRAINT `measurements_files_measurements_cascade`
        FOREIGN KEY (`measurement_id`)
            REFERENCES `seddb`.`measurements` (`id`)
            ON DELETE CASCADE
            ON UPDATE NO ACTION
);


CREATE TABLE IF NOT EXISTS `seddb`.`measurements_sets_subprojects_map`
(
    `id`                 INT UNSIGNED NOT NULL AUTO_INCREMENT,
    `subproject_id`      INT UNSIGNED NOT NULL,
    `measurement_set_id` INT UNSIGNED NOT NULL,
    PRIMARY KEY (`id`),
    CONSTRAINT `measurement_set_subproject_cascade`
        FOREIGN KEY (`subproject_id`)
            REFERENCES `seddb`.`projects_subprojects` (`id`)
            ON DELETE CASCADE
            ON UPDATE NO ACTION
);


# Difam projects
CREATE TABLE IF NOT EXISTS `seddb`.`difam_projects`
(
    `id`                      INT UNSIGNED NOT NULL AUTO_INCREMENT,
    `name`                    VARCHAR(255) NULL     DEFAULT 'Unnamed project',
    `individual_archetype_id` INT UNSIGNED NULL     DEFAULT NULL,
    `owner_id`                INT UNSIGNED NOT NULL,
    `datetime_created`        DATETIME(3)  NOT NULL DEFAULT NOW(3),
    PRIMARY KEY (`id`),
    UNIQUE INDEX `id_UNIQUE` (`id` ASC) VISIBLE
);


CREATE TABLE IF NOT EXISTS `seddb`.`files`
(
    `id`               INT UNSIGNED     NOT NULL AUTO_INCREMENT,
    `temp`             TINYINT UNSIGNED NOT NULL DEFAULT 0,
    `uuid`             VARCHAR(255)     NOT NULL,
    `filename`         VARCHAR(255)     NOT NULL,
    `insert_timestamp` DATETIME(3)      NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
    `directory`        VARCHAR(511)     NOT NULL,
    `owner_id`         INT UNSIGNED     NOT NULL,
    `extension`        VARCHAR(25)      NOT NULL,
    PRIMARY KEY (`id`),
    INDEX `FILES_TEMP` (`temp` ASC) INVISIBLE
);


# CVS projects
CREATE TABLE IF NOT EXISTS `seddb`.`cvs_projects`
(
    `id`               INT UNSIGNED NOT NULL AUTO_INCREMENT,
    `name`             VARCHAR(255) NULL     DEFAULT 'Unnamed project',
    `description`      TEXT         NULL     DEFAULT NULL,
    `owner_id`         INT UNSIGNED NOT NULL,
    `datetime_created` DATETIME(3)  NOT NULL DEFAULT NOW(3),
    PRIMARY KEY (`id`),
    UNIQUE INDEX `id_UNIQUE` (`id` ASC) VISIBLE,
    INDEX `user_cascade_idx` (`owner_id` ASC) VISIBLE,
    CONSTRAINT `user_cvs_project_cascade`
        FOREIGN KEY (`owner_id`)
            REFERENCES `seddb`.`users` (`id`)
            ON DELETE CASCADE
            ON UPDATE NO ACTION
);

# CVS VCS
CREATE TABLE IF NOT EXISTS `seddb`.`cvs_vcss`
(
    `id`               INT UNSIGNED NOT NULL AUTO_INCREMENT,
    `name`             VARCHAR(255) NOT NULL,
    `description`      TEXT         NULL     DEFAULT NULL,
    `project_id`       INT UNSIGNED NOT NULL,
    `datetime_created` DATETIME(3)  NOT NULL DEFAULT NOW(3),
    `year_from`        INT UNSIGNED NOT NULL DEFAULT (YEAR(NOW())),
    `year_to`          INT UNSIGNED NOT NULL DEFAULT (YEAR(NOW() + INTERVAL 6 YEAR)),
    PRIMARY KEY (`id`),
    UNIQUE INDEX `id_UNIQUE` (`id` ASC) VISIBLE,
    INDEX `cvs_project_cascade_idx` (`project_id` ASC) VISIBLE,
    CONSTRAINT `cvs_project_vcs_cascade`
        FOREIGN KEY (`project_id`)
            REFERENCES `seddb`.`cvs_projects` (`id`)
            ON DELETE CASCADE
            ON UPDATE NO ACTION
);

CREATE TABLE IF NOT EXISTS `seddb`.`cvs_vcs_table_rows`
(
    `id`                       INT UNSIGNED NOT NULL AUTO_INCREMENT,
    `row_index`                INT UNSIGNED NOT NULL,
    `vcs_id`                   INT UNSIGNED NOT NULL,
    `iso_process_id`           INT UNSIGNED NULL DEFAULT NULL,
    `subprocess_id`            INT UNSIGNED NULL DEFAULT NULL,
    `stakeholder`              VARCHAR(255) NULL DEFAULT NULL,
    `stakeholder_expectations` TEXT         NULL DEFAULT NULL,
    PRIMARY KEY (`id`),
    UNIQUE INDEX `id_UNIQUE` (`id` ASC) VISIBLE,
    INDEX `vcs_cascade_idx` (`vcs_id` ASC) VISIBLE,
    CONSTRAINT `vcs_cascade`
        FOREIGN KEY (`vcs_id`)
            REFERENCES `seddb`.`cvs_vcss` (`id`)
            ON DELETE CASCADE
            ON UPDATE NO ACTION
);

CREATE TABLE IF NOT EXISTS `seddb`.`cvs_vcs_stakeholder_needs`
(
    `id`           INT UNSIGNED NOT NULL AUTO_INCREMENT,
    `table_row_id` INT UNSIGNED NOT NULL,
    `need`         VARCHAR(255) NULL DEFAULT NULL,
    `rank_weight`  INT UNSIGNED NOT NULL DEFAULT 0,
    PRIMARY KEY (`id`),
    UNIQUE INDEX `id_UNIQUE` (`id` ASC) VISIBLE,
    INDEX `vcs_table_row_cascade_idx` (`table_row_id` ASC) VISIBLE,
    CONSTRAINT `vcs_table_row_cascade`
        FOREIGN KEY (`table_row_id`)
            REFERENCES `seddb`.`cvs_vcs_table_rows` (`id`)
            ON DELETE CASCADE
            ON UPDATE NO ACTION
);

CREATE TABLE IF NOT EXISTS `seddb`.`cvs_vcs_value_drivers`
(
    `id`         INT UNSIGNED NOT NULL AUTO_INCREMENT,
    `name`       VARCHAR(255) NOT NULL,
    `project_id` INT UNSIGNED NOT NULL,
    PRIMARY KEY (`id`),
    UNIQUE INDEX `id_UNIQUE` (`id` ASC) VISIBLE,
    INDEX `cvs_project_cascade_idx` (`project_id` ASC) VISIBLE,
    CONSTRAINT `cvs_project_value_driver_cascade`
        FOREIGN KEY (`project_id`)
            REFERENCES `seddb`.`cvs_projects` (`id`)
            ON DELETE CASCADE
            ON UPDATE NO ACTION
);

CREATE TABLE IF NOT EXISTS `seddb`.`cvs_vcs_needs_divers_map`
(
    `id`                  INT UNSIGNED NOT NULL AUTO_INCREMENT,
    `stakeholder_need_id` INT UNSIGNED NOT NULL,
    `value_driver_id`     INT UNSIGNED NOT NULL,
    PRIMARY KEY (`id`),
    UNIQUE INDEX `id_UNIQUE` (`id` ASC) VISIBLE,
    FOREIGN KEY (`stakeholder_need_id`) REFERENCES `cvs_vcs_stakeholder_needs` (`id`)
        ON DELETE CASCADE,
    FOREIGN KEY (`value_driver_id`) REFERENCES `cvs_vcs_value_drivers` (`id`)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS `seddb`.`cvs_vcs_subprocesses`
(
    `id`                INT UNSIGNED NOT NULL AUTO_INCREMENT,
    `name`              VARCHAR(255) NOT NULL,
    `parent_process_id` INT UNSIGNED NOT NULL,
    `project_id`        INT UNSIGNED NOT NULL,
    PRIMARY KEY (`id`),
    UNIQUE INDEX `id_UNIQUE` (`id` ASC) VISIBLE,
    INDEX `cvs_project_cascade_idx` (`project_id` ASC) VISIBLE,
    CONSTRAINT `cvs_project_subprocess_cascade`
        FOREIGN KEY (`project_id`)
            REFERENCES `seddb`.`cvs_projects` (`id`)
            ON DELETE CASCADE
            ON UPDATE NO ACTION
);

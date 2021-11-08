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
    UNIQUE INDEX `id_UNIQUE` (`id` ASC) VISIBLE
);

# ===================================
# CVS VCS stuff
# ===================================

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
    UNIQUE INDEX `id_UNIQUE` (`id` ASC) VISIBLE
);

CREATE TABLE IF NOT EXISTS `seddb`.`cvs_vcs_table_rows`
(
    `id`                       INT UNSIGNED NOT NULL AUTO_INCREMENT,
    `vcs_id`                   INT UNSIGNED NOT NULL,
    `isoprocess_id`            INT UNSIGNED NULL,
    `subprocess_id`            INT UNSIGNED NULL,
    `stakeholder`              VARCHAR(255) NOT NULL,
    `stakeholder_expectations` TEXT         NULL DEFAULT NULL,
    PRIMARY KEY (`id`),
    UNIQUE INDEX `id_UNIQUE` (`id` ASC) VISIBLE
);

CREATE TABLE IF NOT EXISTS `seddb`.`cvs_vcs_stakeholder_needs`
(
    `id`                       INT UNSIGNED NOT NULL AUTO_INCREMENT,
    `vcs_row_id`               INT UNSIGNED NOT NULL,
    `need`                     VARCHAR(255) NOT NULL,
    `stakeholder_expectations` TEXT         NULL     DEFAULT NULL,
    `rank_weight`              INT UNSIGNED NOT NULL DEFAULT 0,
    PRIMARY KEY (`id`),
    UNIQUE INDEX `id_UNIQUE` (`id` ASC) VISIBLE
);

CREATE TABLE IF NOT EXISTS `seddb`.`cvs_vcs_value_drivers`
(
    `id`         INT UNSIGNED NOT NULL AUTO_INCREMENT,
    `name`       VARCHAR(255) NOT NULL,
    `project_id` INT UNSIGNED NOT NULL,
    PRIMARY KEY (`id`),
    UNIQUE INDEX `id_UNIQUE` (`id` ASC) VISIBLE
);

CREATE TABLE IF NOT EXISTS `seddb`.`cvs_vcs_need2driver`
(
    `id`                  INT UNSIGNED NOT NULL AUTO_INCREMENT, # needed?
    `stakeholder_need_id` INT UNSIGNED NOT NULL,
    `value_driver_id`     INT UNSIGNED NOT NULL,
    PRIMARY KEY (`id`),
    UNIQUE INDEX `id_UNIQUE` (`id` ASC) VISIBLE
);

CREATE TABLE IF NOT EXISTS `seddb`.`cvs_vcs_iso_processes`
(
    `id`       INT UNSIGNED NOT NULL AUTO_INCREMENT,
    `name`     VARCHAR(255) NOT NULL,
    `category` VARCHAR(255) NOT NULL,
    PRIMARY KEY (`id`),
    UNIQUE INDEX `id_UNIQUE` (`id` ASC) VISIBLE
);

# Creating default ISO 15288 processes
INSERT IGNORE INTO cvs_vcs_iso_processes(id, name, category)
VALUES (1, 'Acquisition', 'Agreement Processes'),
       (2, 'Supply', 'Agreement Processes'),

       (3, 'Life-cycle model management', 'Organizational project-enabling processes'),
       (4, 'Infrastructure management', 'Organizational project-enabling processes'),
       (5, 'Project portfolio management', 'Organizational project-enabling processes'),
       (6, 'Human resource management', 'Organizational project-enabling processes'),
       (7, 'Quality management', 'Organizational project-enabling processes'),

       (8, 'Project planning', 'Project processes'),
       (9, 'Project assessment and control', 'Project processes'),
       (10, 'Decision management', 'Project processes'),
       (11, 'Risk management', 'Project processes'),
       (12, 'Configuration management', 'Project processes'),
       (13, 'Information management', 'Project processes'),
       (14, 'Measurement', 'Project processes'),

       (15, 'Stakeholder requirements definition', 'Technical processes'),
       (16, 'Requirements analysis', 'Technical processes'),
       (17, 'Architectual design', 'Technical processes'),
       (18, 'Implementation', 'Technical processes'),
       (19, 'Integration', 'Technical processes'),
       (20, 'Verification', 'Technical processes'),
       (21, 'Transition', 'Technical processes'),
       (22, 'Validation', 'Technical processes'),
       (23, 'Operation', 'Technical processes'),
       (24, 'Maintenance', 'Technical processes'),
       (25, 'Disposal', 'Technical processes');

CREATE TABLE IF NOT EXISTS `seddb`.`cvs_vcs_subprocesses`
(
    `id`                INT UNSIGNED NOT NULL AUTO_INCREMENT,
    `name`              VARCHAR(255) NOT NULL,
    `parent_process_id` INT UNSIGNED NOT NULL,
    PRIMARY KEY (`id`),
    UNIQUE INDEX `id_UNIQUE` (`id` ASC) VISIBLE
);



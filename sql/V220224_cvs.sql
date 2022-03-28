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
    `id`                       INT UNSIGNED AUTO_INCREMENT,
    `node_id`                  INT UNSIGNED NOT NULL,
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
            ON UPDATE NO ACTION,
        FOREIGN KEY(`node_id`)
            REFERENCES `seddb`.`cvs_bpmn_nodes`(`id`)
            ON DELETE CASCADE
            ON UPDATE NO ACTION
);

CREATE TABLE IF NOT EXISTS `seddb`.`cvs_vcs_stakeholder_needs`
(
    `id`           INT UNSIGNED NOT NULL AUTO_INCREMENT,
    `table_row_id` INT UNSIGNED NOT NULL,
    `need`         VARCHAR(255) NULL     DEFAULT NULL,
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
    `unit`       VARCHAR(63) DEFAULT NULL,
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
    `order_index`       INT UNSIGNED NOT NULL,
    PRIMARY KEY (`id`),
    UNIQUE INDEX `id_UNIQUE` (`id` ASC) VISIBLE,
    INDEX `cvs_project_cascade_idx` (`project_id` ASC) VISIBLE,
    CONSTRAINT `cvs_project_subprocess_cascade`
        FOREIGN KEY (`project_id`)
            REFERENCES `seddb`.`cvs_projects` (`id`)
            ON DELETE CASCADE
            ON UPDATE NO ACTION
);
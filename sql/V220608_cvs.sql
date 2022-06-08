
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

#Value Creation Strategies
CREATE TABLE IF NOT EXISTS `seddb`.`cvs_vcss`
(
    `id`               INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `name`             VARCHAR(255) NOT NULL,
    `description`      TEXT         NULL     DEFAULT NULL,
    `datetime_created` DATETIME(3)  NOT NULL DEFAULT NOW(3),
    `year_from`        INT UNSIGNED NOT NULL DEFAULT (YEAR(NOW())),
    `year_to`          INT UNSIGNED NOT NULL DEFAULT (YEAR(NOW() + INTERVAL 6 YEAR)),
    `project`       INT UNSIGNED NOT NULL,
    CONSTRAINT `cvs_project_vcs_cascade`
        FOREIGN KEY (`project`)
            REFERENCES `seddb`.`cvs_projects`(`id`)
            ON DELETE CASCADE
            ON UPDATE NO ACTION
);

#Iso_processes
CREATE TABLE IF NOT EXISTS `seddb`.`cvs_iso_processes`
(
    `name`          TEXT NOT NULL PRIMARY KEY,
    `category`      TEXT NOT NULL   
);

#Subprocesses
CREATE TABLE IF NOT EXISTS `seddb`.`cvs_subprocesses`
(
    `id`            INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `name`          TEXT NOT NULL,
    `order_index`   INT NOT NULL UNIQUE,
    `iso_process`   TEXT NOT NULL REFERENCES `seddb`.`cvs_iso_processes`(`name`)
);

#The rows of the vcs table
CREATE TABLE IF NOT EXISTS `seddb`.`cvs_vcs_rows`
(
    `id`                    INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `index`                 INT UNSIGNED UNIQUE,
    `stakeholder`           TEXT NOT NULL,
    `stakeholder_needs`     TEXT NOT NULL, 
    `stakeholder_expectations` TEXT NOT NULL,
    `iso_process`               TEXT NULL REFERENCES `seddb`.`cvs_iso_processes`(`name`)
    `subprocess`                INT UNSIGNED NULL REFERENCES `seddb`.`cvs_subprocesses`(`id`)
);

#The value dimensions
CREATE TABLE IF NOT EXISTS `seddb`.`cvs_value_dimensions`
(
    `id`            INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `name`          TEXT NOT NULL,
    `priority`      TEXT NOT NULL, 
    `vcs_row`       INT UNSIGNED NOT NULL REFERENCES `seddb`.`cvs_vcs_row`(`id`)
);

#Value drivers
CREATE TABLE IF NOT EXISTS `seddb`.`cvs_value_drivers`
(
    `id`                INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `name`              TEXT NOT NULL,
    `value_dimension`   INT UNSIGNED NULL REFERENCES `seddb`.`cvs_value_dimensions`(`id`)
);

#Vcs row and value driver connection
CREATE TABLE IF NOT EXISTS `seddb`.`rowDrivers`
(
    `vcs_row`       INT UNSIGNED PRIMARY KEY REFERENCES `seddb`.`cvs_vcs_rows`(`id`),
    `value_driver`  INT UNSIGNED PRIMARY KEY REFERENCES `seddb`.`cvs_value_drivers`(`id`)
);

# BPMN node
CREATE TABLE IF NOT EXISTS `seddb`.`cvs_nodes`
(
    `id`                INT UNSIGNED AUTO_INCREMENT,
    `vcs`               INT UNSIGNED NOT NULL,
    `from`              INT UNSIGNED,
    `to`                INT UNSIGNED,
    `pos_x`             INT UNSIGNED NOT NULL,
    `pos_y`             INT UNSIGNED NOT NULL,
    PRIMARY KEY (`id`),
    FOREIGN KEY(`vcs`)
        REFERENCES `seddb`.`cvs_vcss` (`id`)
        ON DELETE CASCADE,
    FOREIGN KEY (`from`)
        REFERENCES `seddb`.`cvs_nodes` (`id`)
        ON DELETE CASCADE,
    FOREIGN KEY (`to`)
        REFERENCES `seddb`.`cvs_nodes` (`id`)
        ON DELETE CASCADE
);

# BPMN start/stop node
CREATE TABLE IF NOT EXISTS `seddb`.`cvs_start_stop_nodes`
(
    `id`           INT UNSIGNED NOT NULL REFERENCES `seddb`.`cvs_nodes`(`id`),
    `type`         VARCHAR(4),
    PRIMARY KEY (`id`),
    CONSTRAINT `check_type` CHECK (`type` IN ('start', 'stop'))
);

# BPMN process node
CREATE TABLE IF NOT EXISTS  `seddb`.`cvs_process_node`
(
    `id`            INT UNSIGNED NOT NULL REFERENCES `seddb`.`cvs_nodes`(`id`),
    `vcs_row`       INT UNSIGNED NOT NULL,
    FOREIGN KEY (`iso_process`)
        REFERENCES `seddb`.`cvs_iso_process` (`id`)
        ON DELETE CASCADE
);
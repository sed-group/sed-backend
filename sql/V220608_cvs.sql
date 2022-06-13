
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
    `id`            INT UNSIGNED NOT NULL PRIMARY KEY,
    `name`          VARCHAR(255) NOT NULL,
    `category`      TEXT NOT NULL   
);

#Subprocesses
CREATE TABLE IF NOT EXISTS `seddb`.`cvs_subprocesses`
(
    `id`            INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `name`          TEXT NOT NULL,
    `order_index`   INT NOT NULL UNIQUE, #TODO ask if it is neccessary to rearrange subprocesses in modal window
    `iso_process`   INT UNSIGNED NOT NULL,
     CONSTRAINT `fk_iso_process_subprocess` 
        FOREIGN KEY (`iso_process`) 
	    REFERENCES `seddb`.`cvs_iso_processes`(`id`) 
	    ON DELETE CASCADE
	    ON UPDATE NO ACTION
);

#The rows of the vcs table
CREATE TABLE IF NOT EXISTS `seddb`.`cvs_vcs_rows`
(
    `id`                    INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `index`                 INT UNSIGNED UNIQUE,
    `stakeholder`           TEXT NOT NULL,
    `stakeholder_needs`     TEXT NOT NULL, 
    `stakeholder_expectations` TEXT NOT NULL,
    `iso_process`               INT UNSIGNED NULL,
    `subprocess`                INT UNSIGNED NULL,
    `vcs`                       INT UNSIGNED NOT NULL,
    CONSTRAINT `row_iso_process`
        FOREIGN KEY (`iso_process`) 
        REFERENCES `seddb`.`cvs_iso_processes`(`id`)
	    ON DELETE CASCADE
	    ON UPDATE NO ACTION,
    CONSTRAINT `row_subprocess`
        FOREIGN KEY (`subprocess`) 
        REFERENCES `seddb`.`cvs_subprocesses`(`id`)
	    ON DELETE CASCADE
	    ON UPDATE NO ACTION,
    CONSTRAINT `row_vcs`
        FOREIGN KEY(`vcs`)
        REFERENCES  `seddb`.`cvs_vcss`(`id`)
        ON DELETE CASCADE
        ON UPDATE NO ACTION
);

#The value dimensions
CREATE TABLE IF NOT EXISTS `seddb`.`cvs_value_dimensions`
(
    `id`            INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `name`          TEXT NOT NULL,
    `priority`      TEXT NOT NULL, 
    `vcs_row`       INT UNSIGNED NOT NULL,
    CONSTRAINT `row_dimensions`
    FOREIGN KEY (`vcs_row`) 
    REFERENCES `seddb`.`cvs_vcs_rows`(`id`)
    ON DELETE CASCADE
);

#Value drivers
CREATE TABLE IF NOT EXISTS `seddb`.`cvs_value_drivers`
(
    `id`                INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `name`              TEXT NOT NULL,
    `value_dimension`   INT UNSIGNED NULL,
    CONSTRAINT `driver_dimension` 
    FOREIGN KEY (`value_dimension`) 
    REFERENCES `seddb`.`cvs_value_dimensions`(`id`)
    ON DELETE CASCADE
);

#Vcs row and value driver connection
CREATE TABLE IF NOT EXISTS `seddb`.`cvs_rowDrivers`
(
    `vcs_row`       INT UNSIGNED, 
    `value_driver`  INT UNSIGNED, 
    PRIMARY KEY (`vcs_row`, `value_driver`),
    FOREIGN KEY (`vcs_row`) REFERENCES `seddb`.`cvs_vcs_rows`(`id`)
    ON DELETE CASCADE,
    FOREIGN KEY (`value_driver`) REFERENCES `seddb`.`cvs_value_drivers`(`id`)
    ON DELETE CASCADE
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


CREATE TABLE IF NOT EXISTS `seddb`.`cvs_designs`
(
    `id`                INT UNSIGNED NOT NULL AUTO_INCREMENT,
    `name`              VARCHAR(255) NOT NULL,
    `description`       TEXT DEFAULT NULL,
    `vcs`               INT UNSIGNED NOT NULL,
    PRIMARY KEY(`id`),
    FOREIGN KEY(`vcs`)
        REFERENCES `seddb`.`cvs_vcss`(`id`)
);

CREATE TABLE IF NOT EXISTS `seddb`.`cvs_quantified_objectives`
(
    `id`                INT UNSIGNED NOT NULL AUTO_INCREMENT,
    `name`              VARCHAR(63) NOT NULL,
    `value`             DOUBLE NOT NULL,
    `unit`              VARCHAR(63) NOT NULL,
    `value_driver`      INT UNSIGNED NOT NULL,
    `design`            INT UNSIGNED NOT NULL,
    PRIMARY KEY(`id`),
    FOREIGN KEY(`design`)
        REFERENCES `seddb`.`cvs_designs`(`id`),
    FOREIGN KEY(`value_driver`)
        REFERENCES `seddb`.`cvs_value_drivers`(`id`)
);

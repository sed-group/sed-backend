
# CVS projects
CREATE TABLE IF NOT EXISTS `seddb`.`cvs_projects`
(
    `id`               INT UNSIGNED NOT NULL AUTO_INCREMENT,
    `name`             VARCHAR(255) NULL     DEFAULT 'Unnamed project',
    `description`      TEXT         NULL     DEFAULT NULL,
    `currency`         VARCHAR(10)   NULL     DEFAULT '€',
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
    `vcs`           INT UNSIGNED NOT NULL,
    `name`          TEXT NOT NULL,
    `order_index`   INT, #TODO ask if it is neccessary to rearrange subprocesses in modal window
    `iso_process`   INT UNSIGNED NOT NULL,
    FOREIGN KEY (`iso_process`)
        REFERENCES `seddb`.`cvs_iso_processes`(`id`)
	    ON DELETE CASCADE,
    FOREIGN KEY(`vcs`) REFERENCES  `seddb`.`cvs_vcss`(`id`)
        ON DELETE CASCADE

);

#The rows of the vcs table
CREATE TABLE IF NOT EXISTS `seddb`.`cvs_vcs_rows`
(
    `id`                        INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `vcs`                       INT UNSIGNED NOT NULL,
    `index`                     INT UNSIGNED NOT NULL,
    `stakeholder`               TEXT NOT NULL,
    `stakeholder_expectations`  TEXT NOT NULL,
    `iso_process`               INT UNSIGNED NULL,
    `subprocess`                INT UNSIGNED NULL,
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
    # CONSTRAINT `unique_index`
      #  UNIQUE (`index`, `vcs`)
);

# Stakeholder need
CREATE TABLE IF NOT EXISTS `seddb`.`cvs_stakeholder_needs`
(
    `id`                INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    `vcs_row`           INT UNSIGNED NOT NULL,
    `need`              TEXT NOT NULL,
    `value_dimension`   TEXT NULL,
    `rank_weight`       FLOAT NULL,
    FOREIGN KEY(`vcs_row`)
        REFERENCES  `seddb`.`cvs_vcs_rows`(`id`)
        ON DELETE CASCADE,
    CONSTRAINT check_weight
        check (`rank_weight` between 0 and 1)
);

#The value dimensions - not to be used
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
    `user`              INT UNSIGNED NOT NULL,
    `name`              TEXT NOT NULL,
    `unit`              VARCHAR(10) NULL,
    FOREIGN KEY(`user`)
        REFERENCES  `seddb`.`users`(`id`)
        ON DELETE CASCADE
);

#Vcs row and value driver connection
CREATE TABLE IF NOT EXISTS `seddb`.`cvs_vcs_need_drivers`
(
    `stakeholder_need`  INT UNSIGNED,
    `value_driver`      INT UNSIGNED,
    PRIMARY KEY (`stakeholder_need`, `value_driver`),
    FOREIGN KEY (`stakeholder_need`)
        REFERENCES `seddb`.`cvs_stakeholder_needs`(`id`)
        ON DELETE CASCADE,
    FOREIGN KEY (`value_driver`)
        REFERENCES `seddb`.`cvs_value_drivers`(`id`)
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
    `id`           INT UNSIGNED NOT NULL,
    `type`         VARCHAR(5),
    PRIMARY KEY (`id`),
    FOREIGN KEY (`id`) REFERENCES `seddb`.`cvs_nodes`(`id`)
        ON DELETE CASCADE,
    CONSTRAINT `check_type` CHECK (`type` IN ('start', 'stop'))
);

# BPMN process node
CREATE TABLE IF NOT EXISTS  `seddb`.`cvs_process_nodes`
(
    `id`            INT UNSIGNED NOT NULL,
    `vcs_row`       INT UNSIGNED NOT NULL,
    PRIMARY KEY (`id`),
    FOREIGN KEY (`id`) REFERENCES `seddb`.`cvs_nodes`(`id`)
        ON DELETE CASCADE,
    FOREIGN KEY (`vcs_row`)
        REFERENCES `seddb`.`cvs_vcs_rows` (`id`)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS `seddb`.`cvs_design_groups`
(
    `id`                INT UNSIGNED NOT NULL AUTO_INCREMENT,
    `project`           INT UNSIGNED NOT NULL,
    `name`              VARCHAR(255) NOT NULL,
    PRIMARY KEY(`id`),
    FOREIGN KEY(`project`)
        REFERENCES `seddb`.`cvs_projects`(`id`)
        ON DELETE CASCADE
);

CREATE TABLE `seddb`.`cvs_design_group_drivers`
(
    `design_group`      INT UNSIGNED NOT NULL, 
    `value_driver`      INT UNSIGNED NOT NULL,
    PRIMARY KEY(`design_group`, `value_driver`),
    FOREIGN KEY (`design_group`)
        REFERENCES `seddb`.`cvs_design_groups`(`id`)
        ON DELETE CASCADE,
    FOREIGN KEY (`value_driver`)
        REFERENCES `seddb`.`cvs_value_drivers`(`id`)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS `seddb`.`cvs_designs`
(
    `id`                INT UNSIGNED NOT NULL AUTO_INCREMENT,
    `design_group`      INT UNSIGNED NOT NULL,
    `name`              VARCHAR(255) NOT NULL,
    PRIMARY KEY(`id`),
    FOREIGN KEY(`design_group`)
        REFERENCES `seddb`.`cvs_design_groups`(`id`)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS `seddb`.`cvs_vd_design_values`
(
    `value_driver`      INT UNSIGNED NOT NULL,
    `design`            INT UNSIGNED NOT NULL,
    `value`             FLOAT NOT NULL,
    PRIMARY KEY(`value_driver`, `design`),
    FOREIGN KEY(`value_driver`)
        REFERENCES `seddb`.`cvs_value_drivers`(`id`)
        ON DELETE CASCADE,
    FOREIGN KEY(`design`)
        REFERENCES `seddb`.`cvs_designs`(`id`)
        ON DELETE CASCADE
);

"""
CREATE TABLE IF NOT EXISTS `seddb`.`cvs_quantified_objectives`
(
    `value_driver`      INT UNSIGNED NOT NULL,
    `design_group`      INT UNSIGNED NOT NULL,
    `name`              VARCHAR(63) NOT NULL,
    `unit`              VARCHAR(63) NOT NULL,
    PRIMARY KEY(`value_driver`, `design_group`),
    FOREIGN KEY(`design_group`)
        REFERENCES `seddb`.`cvs_design_groups`(`id`)
        ON DELETE CASCADE,
    FOREIGN KEY(`value_driver`)
        REFERENCES `seddb`.`cvs_value_drivers`(`id`)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS `seddb`.`cvs_quantified_objective_values`
(
    `design`            INT UNSIGNED NOT NULL,
    `value_driver`      INT UNSIGNED NOT NULL,
    `design_group`      INT UNSIGNED NOT NULL,
    `value`             FLOAT,
    PRIMARY KEY(`design`, `value_driver`, `design_group`),
    FOREIGN KEY(`design`)
        REFERENCES `seddb`.`cvs_designs`(`id`)
        ON DELETE CASCADE,
    FOREIGN KEY(`design_group`)
        REFERENCES `seddb`.`cvs_design_groups`(`id`)
        ON DELETE CASCADE,
    FOREIGN KEY(`value_driver`)
        REFERENCES `seddb`.`cvs_value_drivers`(`id`)
        ON DELETE CASCADE
);
"""

CREATE TABLE IF NOT EXISTS `seddb`.`cvs_design_mi_formulas`
(
    `vcs_row`           INT UNSIGNED NOT NULL,
    `time`              TEXT,
    `time_unit`         VARCHAR(5),
    `cost`              TEXT,
    `revenue`           TEXT,
    `rate`              TEXT,
    PRIMARY KEY (`vcs_row`),
    FOREIGN KEY(`vcs_row`)
        REFERENCES `seddb`.`cvs_vcs_rows`(`id`)
        ON DELETE CASCADE,
    CONSTRAINT `check_unit` CHECK (`time_unit` IN ('HOUR', 'DAY', 'WEEK', 'MONTH', 'YEAR')),
    CONSTRAINT `check_rate` CHECK (`rate` IN ('per_product', 'per_project'))
);

CREATE TABLE IF NOT EXISTS `seddb`.`cvs_market_inputs`
(
    `id`            INT UNSIGNED NOT NULL AUTO_INCREMENT,
    `project`       INT UNSIGNED NOT NULL,
    `name`          TEXT NOT NULL,
    `unit`          TEXT NOT NULL,
    PRIMARY KEY(`id`),
    FOREIGN KEY(`project`)
        REFERENCES `seddb`.`cvs_projects`(`id`)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS `seddb`.`cvs_market_values`
(
    `vcs`           INT UNSIGNED NOT NULL,
    `market_input`  INT UNSIGNED NOT NULL,
    `value`         FLOAT NOT NULL,
    PRIMARY KEY(`vcs`,`market_input`),
    FOREIGN KEY(`vcs`)
        REFERENCES `seddb`.`cvs_vcss`(`id`)
        ON DELETE CASCADE,
    FOREIGN KEY(`market_input`)
        REFERENCES `seddb`.`cvs_market_inputs`(`id`)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS `seddb`.`cvs_formulas_market_inputs`
(
    `formulas`      INT UNSIGNED NOT NULL,
    `market_input`  INT UNSIGNED NOT NULL,
    PRIMARY KEY(`formulas`, `market_input`),
    FOREIGN KEY (`formulas`)
        REFERENCES `seddb`.`cvs_design_mi_formulas`(`vcs_row`)
        ON DELETE CASCADE,
    FOREIGN KEY(`market_input`)
        REFERENCES `seddb`.`cvs_market_inputs`(`id`)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS `seddb`.`cvs_formulas_quantified_objectives`
(
    `formulas`      INT UNSIGNED NOT NULL,
    `value_driver`      INT UNSIGNED NOT NULL,
    `design_group`      INT UNSIGNED NOT NULL,
    PRIMARY KEY(`formulas`, `value_driver`, `design_group`),
    FOREIGN KEY (`formulas`)
        REFERENCES `seddb`.`cvs_design_mi_formulas`(`vcs_row`)
        ON DELETE CASCADE,
    FOREIGN KEY(`value_driver`, `design_group`)
        REFERENCES `seddb`.`cvs_quantified_objectives`(`value_driver`, `design_group`)
        ON DELETE CASCADE
);
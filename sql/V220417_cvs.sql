CREATE TABLE IF NOT EXISTS `seddb`.`cvs_vcs_value_drivers`
(
    `id`         INT UNSIGNED NOT NULL AUTO_INCREMENT,
    `name`       VARCHAR(255) NOT NULL,
    `unit`       VARCHAR(63) NOT NULL,
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

CREATE TABLE IF NOT EXISTS `seddb`.`cvs_bpmn_nodes`
(
    `id`                INT NOT NULL AUTO_INCREMENT,
    `vcs_id`            INT NOT NULL REFERENCES `seddb`.`cvs_vcss`(`id`),
    `name`              VARCHAR(255) NOT NULL,
    `type`              VARCHAR(63) NOT NULL,
    `posX`              INT UNSIGNED,
    `posY`              INT UNSIGNED,
    PRIMARY KEY(`id`)
);

CREATE TABLE IF NOT EXISTS `seddb`.`cvs_bpmn_edges`
(
    `id`                INT NOT NULL AUTO_INCREMENT,
    `name`              VARCHAR(255) NOT NULL,
    `vcs_id`            INT NOT NULL REFERENCES `seddb`.`cvs_vcss`(`id`),
    `from`              INT NOT NULL REFERENCES `seddb`.`cvs_bpmn_nodes`(`id`),
    `to`                INT NOT NULL REFERENCES `seddb`.`cvs_bpmn_nodes`(`id`),
    `probability`       INT,
    PRIMARY KEY(`id`)
);

CREATE TABLE IF NOT EXISTS `seddb`.`designs`
(
    `id`                INT UNSIGNED NOT NULL AUTO_INCREMENT,
    `project`           INT UNSIGNED NOT NULL,
    `vcs`               INT UNSIGNED NOT NULL,
    `name`              VARCHAR(255) NOT NULL,
    `description`       TEXT DEFAULT NULL,
    PRIMARY KEY(`id`),
    FOREIGN KEY(`project`)
        REFERENCES `seddb`.`cvs_projects`(`id`),
    FOREIGN KEY(`vcs`)
        REFERENCES `seddb`.`cvs_vcss`(`id`)
);

CREATE TABLE IF NOT EXISTS `seddb`.`value_driver_props`
(
    `id`                INT UNSIGNED NOT NULL AUTO_INCREMENT,
    `design`            INT UNSIGNED NOT NULL,
    `value_driver`      INT UNSIGNED NOT NULL,
    `property`          DOUBLE NOT NULL,
    PRIMARY KEY(`id`),
    FOREIGN KEY(`design`)
        REFERENCES `seddb`.`designs`(`id`),
    FOREIGN KEY(`value_driver`)
        REFERENCES `seddb`.`cvs_vcs_value_drivers`(`id`)
);
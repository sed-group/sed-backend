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
    `from`              INT NOT NULL REFERENCES `seddb`.`cvs_bpmn_nodes`(id),
    `to`                INT NOT NULL REFERENCES `seddb`.`cvs_bpmn_nodes`(id),
    `probability`       INT,
    PRIMARY KEY(`id`)
);
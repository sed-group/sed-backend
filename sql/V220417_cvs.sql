
CREATE TABLE IF NOT EXISTS `seddb`.`cvs_bpmn_nodes`
(
    `id`                INT UNSIGNED NOT NULL AUTO_INCREMENT,
    `vcs_id`            INT UNSIGNED NOT NULL,
    `name`              VARCHAR(255) NOT NULL,
    `type`              VARCHAR(63) NOT NULL,
    `pos_x`             INT UNSIGNED,
    `pos_y`             INT UNSIGNED,
    PRIMARY KEY(`id`),
    FOREIGN KEY(`vcs_id`)
        REFERENCES `seddb`.`cvs_vcss`(`id`)
        ON DELETE CASCADE
);


CREATE TABLE IF NOT EXISTS `seddb`.`cvs_bpmn_edges`
(
    `id`                INT NOT NULL AUTO_INCREMENT,
    `vcs_id`            INT UNSIGNED NOT NULL,
    `name`              VARCHAR(255) NOT NULL,
    `from_node`         INT NOT NULL,
    `to_node`           INT NOT NULL,
    `probability`       INT,
    PRIMARY KEY(`id`),
    FOREIGN KEY(`from_node`)
        REFERENCES `seddb`.`cvs_bpmn_nodes`(`id`),
    FOREIGN KEY(`from_node`)
        REFERENCES `seddb`.`cvs_bpmn_nodes`(`id`),
    FOREIGN KEY(`vcs_id`)
        REFERENCES `seddb`.`cvs_vcss`(`id`)
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

CREATE TABLE IF NOT EXISTS `seddb`.`quantified_objectives`
(
    `id`                INT UNSIGNED NOT NULL AUTO_INCREMENT,
    `design`            INT UNSIGNED NOT NULL,
    `value_driver`      INT UNSIGNED NOT NULL,
    `name`              VARCHAR(63) NOT NULL,
    `property`          DOUBLE NOT NULL,
    `unit`              VARCHAR(63) NOT NULL,
    PRIMARY KEY(`id`),
    FOREIGN KEY(`design`)
        REFERENCES `seddb`.`designs`(`id`),
    FOREIGN KEY(`value_driver`)
        REFERENCES `seddb`.`cvs_vcs_value_drivers`(`id`)
);


CREATE TABLE IF NOT EXISTS `seddb`.`cvs_designs`
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

CREATE TABLE IF NOT EXISTS `seddb`.`cvs_quantified_objectives`
(
    `id`                INT UNSIGNED NOT NULL AUTO_INCREMENT,
    `design`            INT UNSIGNED NOT NULL,
    `value_driver`      INT UNSIGNED NOT NULL,
    `name`              VARCHAR(63) NOT NULL,
    `property`          DOUBLE NOT NULL,
    `unit`              VARCHAR(63) NOT NULL,
    PRIMARY KEY(`id`),
    FOREIGN KEY(`design`)
        REFERENCES `seddb`.`cvs_designs`(`id`),
    FOREIGN KEY(`value_driver`)
        REFERENCES `seddb`.`cvs_vcs_value_drivers`(`id`)
);

CREATE TABLE IF NOT EXISTS `seddb`.`cvs_market_input`
(
    `id`                INT UNSIGNED NOT NULL AUTO_INCREMENT,
    `vcs`               INT UNSIGNED NOT NULL,
    `node`              INT UNSIGNED NOT NULL,
    `time`              DOUBLE,
    `cost`              DOUBLE,
    `revenue`           DOUBLE,
    PRIMARY KEY (`id`),
    FOREIGN KEY(`vcs`)
        REFERENCES `seddb`.`cvs_vcss`(`id`),
    FOREIGN KEY(`node`)
        REFERENCES `seddb`.`cvs_bpmn_nodes`(`id`)
)

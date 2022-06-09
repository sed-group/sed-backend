





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

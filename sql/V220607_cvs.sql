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
    `id`           INT NOT NULL REFERENCES `seddb`.`cvs_nodes`(`id`),
    `type`              VARCHAR(4),
    PRIMARY KEY (`id`),
    CONSTRAINT `check_type` CHECK (`type` IN ('start', 'stop'))
);

# BPMN process node
CREATE TABLE IF NOT EXISTS  `seddb`.`cvs_process_node`
(
    `id`            INT NOT NULL REFERENCES `seddb`.`cvs_nodes`(`id`),
    `iso_process`   INT NOT NULL,
    FOREIGN KEY (`iso_process`)
        REFERENCES `seddb`.`cvs_iso_process` (`id`)
        ON DELETE CASCADE
);

# BPMN subprocess node
CREATE TABLE IF NOT EXISTS  `seddb`.`cvs_subprocess_node`
(
    `id`            INT NOT NULL REFERENCES `seddb`.`cvs_nodes`(`id`),
    `subprocess`    INT NOT NULL,
    FOREIGN KEY (`subprocess`)
        REFERENCES `seddb`.`cvs_subprocess` (`id`)
        ON DELETE CASCADE
)

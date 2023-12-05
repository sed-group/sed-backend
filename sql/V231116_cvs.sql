CREATE TABLE IF NOT EXISTS `seddb`.`cvs_simulation_files`
(
    `project_id` INT UNSIGNED NOT NULL,
    `file` INT UNSIGNED NOT NULL,
    `insert_timestamp` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
    `vs_x_ds` TEXT NOT NULL,
    PRIMARY KEY (`file`),
    FOREIGN KEY (`project_id`)
        REFERENCES `seddb`.`cvs_projects`(`id`)
        ON DELETE CASCADE,
    FOREIGN KEY(`file`)
      REFERENCES `seddb`.`files`(`id`)
      ON DELETE CASCADE
);
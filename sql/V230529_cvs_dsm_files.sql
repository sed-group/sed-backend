CREATE TABLE IF NOT EXISTS `seddb`.`cvs_dsm_files`
(
    `vcs_id` INT UNSIGNED NOT NULL,
    `file_id` INT UNSIGNED NOT NULL,
    PRIMARY KEY (`vcs_id`),
    FOREIGN KEY (`vcs_id`)
        REFERENCES `seddb`.`cvs_vcss`(`id`)
        ON DELETE CASCADE,
    FOREIGN KEY(`file_id`)
      REFERENCES `seddb`.`files`(`id`)
      ON DELETE CASCADE
);
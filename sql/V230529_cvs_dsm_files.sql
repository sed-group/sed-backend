CREATE TABLE IF NOT EXISTS `seddb`.`cvs_dsm_files`
(
    `vcs` INT UNSIGNED NOT NULL,
    `file` INT UNSIGNED NOT NULL,
    PRIMARY KEY (`vcs`),
    FOREIGN KEY (`vcs`)
        REFERENCES `seddb`.`cvs_vcss`(`id`)
        ON DELETE CASCADE,
    FOREIGN KEY(`file`)
      REFERENCES `seddb`.`files`(`id`)
      ON DELETE CASCADE
);
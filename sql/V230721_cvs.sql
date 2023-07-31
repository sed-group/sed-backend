# Value driver to project relation
CREATE TABLE IF NOT EXISTS `seddb`.`cvs_project_value_drivers`
(
    `project`           INT UNSIGNED NOT NULL,
    `value_driver`      INT UNSIGNED NOT NULL,
    PRIMARY KEY (`project`, `value_driver`),
    FOREIGN KEY (`project`)
        REFERENCES `seddb`.`cvs_projects`(`id`)
        ON DELETE CASCADE,
    FOREIGN KEY (`value_driver`)
        REFERENCES `seddb`.`cvs_value_drivers`(`id`)
        ON DELETE CASCADE
);
CREATE UNIQUE INDEX `project_value_driver_index` ON `seddb`.`cvs_project_value_drivers`  (project, value_driver);
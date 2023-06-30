# Additions and modifications to the database as of sed-backend version 1.0.4

# Map files to subprojects
CREATE TABLE IF NOT EXISTS `seddb`.`files_subprojects_map` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `file_id` INT UNSIGNED NOT NULL,
  `subproject_id` INT UNSIGNED NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `id_UNIQUE` (`id` ASC) VISIBLE,
  CONSTRAINT `remove_subproject_to_file_map_on_file_removal`
      FOREIGN KEY (`file_id`)
      REFERENCES `seddb`.`files` (`id`)
      ON DELETE CASCADE
      ON UPDATE NO ACTION,
  CONSTRAINT `remove_subproject_to_file_map_on_subproject_removal`
      FOREIGN KEY (`subproject_id`)
      REFERENCES `seddb`.`projects_subprojects` (`id`)
      ON DELETE CASCADE
      ON UPDATE NO ACTION
      );

# Add name and date fields to subprojects to simplify identification and searchability
ALTER TABLE `seddb`.`projects_subprojects`
    ADD COLUMN `name` VARCHAR(255) NOT NULL DEFAULT 'Unnamed sub-project' AFTER `id`,
    ADD COLUMN `datetime_created` DATETIME(3) NOT NULL DEFAULT NOW(3) AFTER `owner_id`;


# Add date field to projects to simplify identification and searchability
ALTER TABLE `seddb`.`projects`
    ADD COLUMN `datetime_created` DATETIME(3) NOT NULL DEFAULT NOW(3) AFTER `name`;

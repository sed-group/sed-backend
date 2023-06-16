# subprojects are now allowed to have no project_id (null), meaning that they are only accessible to the owner
ALTER TABLE `seddb`.`projects_subprojects`
DROP FOREIGN KEY `projects_cascade`;
ALTER TABLE `seddb`.`projects_subprojects`
ADD CONSTRAINT `projects_cascade`
  FOREIGN KEY (`project_id`)
  REFERENCES `seddb`.`projects` (`id`)
  ON DELETE SET NULL;
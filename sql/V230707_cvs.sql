SET FOREIGN_KEY_CHECKS=0;
ALTER TABLE `seddb`.`cvs_subprocesses`
    ADD COLUMN `project` INT UNSIGNED NOT NULL AFTER `id`,
    MODIFY COLUMN `name` VARCHAR(64),
    DROP FOREIGN KEY `cvs_subprocesses_ibfk_2`,
	DROP COLUMN `vcs`;
SET FOREIGN_KEY_CHECKS=1;

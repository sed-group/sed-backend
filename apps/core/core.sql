# Create schema
CREATE SCHEMA IF NOT EXISTS `seddb` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;

USE seddb;

# Create user with read write access

CREATE USER IF NOT EXISTS 'rw' IDENTIFIED BY 'DONT_USE_IN_PRODUCTION!';
GRANT SELECT, INSERT, UPDATE, DELETE ON * TO 'rw';
GRANT EXECUTE ON `seddb`.* TO 'rw'@'%';

# Create users TABLE
CREATE TABLE IF NOT EXISTS `seddb`.`users` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `username` VARCHAR(45) NOT NULL,
  `password` VARCHAR(100) NOT NULL,
  `email` VARCHAR(100) NULL,
  `full_name` VARCHAR(255) NULL,
  `scopes` VARCHAR(500) NULL DEFAULT '',
  `disabled` TINYINT UNSIGNED NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `id_UNIQUE` (`id` ASC) VISIBLE,
  UNIQUE INDEX `username_UNIQUE` (`username` ASC) VISIBLE);
# TODO: Index users

# Create default admin user
INSERT INTO `seddb`.`users` (`username`, `password`,`scopes`, `disabled`) VALUES ('admin', '$2b$12$HrAma.HCdIFuHtnbVcle/efa9luh.XUqZapqFEUISj91TKTN6UgR6', 'admin', False);

# Create projects table
CREATE TABLE IF NOT EXISTS `seddb`.`projects` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(255) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `id_UNIQUE` (`id` ASC) VISIBLE);

CREATE TABLE IF NOT EXISTS `seddb`.`projects_participants` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `user_id` INT UNSIGNED NOT NULL,
  `project_id` INT UNSIGNED NOT NULL,
  `access_level` INT UNSIGNED NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `id_UNIQUE` (`id` ASC) VISIBLE);

# Remove participants from a project that has been removed
ALTER TABLE `seddb`.`projects_participants`
ADD CONSTRAINT `project_cascade`
  FOREIGN KEY (`project_id`)
  REFERENCES `seddb`.`projects` (`id`)
  ON DELETE CASCADE
  ON UPDATE NO ACTION;

# Remove participant from projects if that user is removed
ALTER TABLE `seddb`.`projects_participants`
ADD INDEX `user_cascade_idx` (`user_id` ASC) VISIBLE;
ALTER TABLE `seddb`.`projects_participants`
ADD CONSTRAINT `user_cascade`
  FOREIGN KEY (`user_id`)
  REFERENCES `seddb`.`users` (`id`)
  ON DELETE CASCADE
  ON UPDATE NO ACTION;

CREATE TABLE IF NOT EXISTS `seddb`.`projects_subprojects` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `application_sid` VARCHAR(255) NOT NULL,
  `project_id` INT UNSIGNED NULL DEFAULT NULL,
  `native_project_id` INT UNSIGNED NOT NULL,
  `owner_id` INT UNSIGNED NOT NULL,
  PRIMARY KEY (`id`),
  INDEX `NATIVE_SUBPROJ_ID` (`native_project_id` ASC) INVISIBLE,
  INDEX `projects_cascade_idx` (`project_id` ASC) VISIBLE,
  CONSTRAINT `projects_cascade`
  FOREIGN KEY (`project_id`)
  REFERENCES `seddb`.`projects` (`id`)
  ON DELETE CASCADE);

# Create individuals table
CREATE TABLE IF NOT EXISTS `seddb`.`individuals` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(255) NOT NULL DEFAULT 'Unnamed individuals',
  `is_archetype` TINYINT UNSIGNED NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `id_UNIQUE` (`id` ASC) VISIBLE);

# Create parameter table
CREATE TABLE IF NOT EXISTS `seddb`.`individuals_parameters` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(255) NOT NULL,
  `value` VARCHAR(255) NULL DEFAULT NULL,
  `type` TINYINT UNSIGNED NOT NULL,
  `individual_id` INT UNSIGNED NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `id_UNIQUE` (`id` ASC) VISIBLE,
  INDEX `individuals_cascade_idx` (`individual_id` ASC) VISIBLE,
  CONSTRAINT `individuals_cascade`
    FOREIGN KEY (`individual_id`)
    REFERENCES `seddb`.`individuals` (`id`)
    ON DELETE CASCADE
    ON UPDATE NO ACTION);


# Create individual to archetypes map
CREATE TABLE IF NOT EXISTS `seddb`.`individuals_archetypes_map` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `individual_archetype_id` INT UNSIGNED NOT NULL,
  `individual_id` INT UNSIGNED NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `id_UNIQUE` (`id` ASC) VISIBLE,
  INDEX `individual_cascade_idx` (`individual_id` ASC) VISIBLE,
  CONSTRAINT `individual_cascade`
    FOREIGN KEY (`individual_id`)
    REFERENCES `seddb`.`individuals` (`id`)
    ON DELETE CASCADE
    ON UPDATE NO ACTION);


CREATE TABLE IF NOT EXISTS `seddb`.`measurements_sets` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(255) NOT NULL DEFAULT 'Unnamed measurement set',
  `type` TINYINT UNSIGNED NOT NULL DEFAULT 0,
  `description` TEXT NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `id_UNIQUE` (`id` ASC) VISIBLE);


# Measurements table
CREATE TABLE IF NOT EXISTS `seddb`.`measurements` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(255) NOT NULL DEFAULT 'Unnamed measurement',
  `type` TINYINT UNSIGNED NOT NULL,
  `description` TEXT NULL,
  `measurement_set_id` INT UNSIGNED NOT NULL,
  PRIMARY KEY (`id`),
  INDEX `measurement_set_cascade_idx` (`measurement_set_id` ASC) VISIBLE,
  CONSTRAINT `measurement_set_cascade`
      FOREIGN KEY (`measurement_set_id`)
      REFERENCES `seddb`.`measurements_sets` (`id`)
      ON DELETE CASCADE
      ON UPDATE NO ACTION);


# Measurement data table
CREATE TABLE IF NOT EXISTS `seddb`.`measurements_results_data` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `measurement_id` INT UNSIGNED NOT NULL,
  `individual_id` INT UNSIGNED,
  `value` VARCHAR(255) NOT NULL,
  `type` TINYINT UNSIGNED NOT NULL,
  `insert_timestamp` DATETIME(3) NOT NULL DEFAULT NOW(3),
  `measurement_timestamp` DATETIME(3) NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `id_UNIQUE` (`id` ASC) VISIBLE,
  INDEX `measurement_data_measurements_cascade_idx` (`measurement_id` ASC) VISIBLE,
  CONSTRAINT `measurement_data_measurements_cascade`
    FOREIGN KEY (`measurement_id`)
    REFERENCES `seddb`.`measurements` (`id`)
    ON DELETE CASCADE
    ON UPDATE NO ACTION);

# Measurements result files table
CREATE TABLE IF NOT EXISTS `seddb`.`measurements_results_files` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `measurement_id` INT UNSIGNED NOT NULL,
  `individual_id` INT UNSIGNED,
  `file` VARCHAR(500) NOT NULL,
  `insert_timestamp` DATETIME(3) NOT NULL DEFAULT NOW(3),
  PRIMARY KEY (`id`),
  UNIQUE INDEX `id_UNIQUE` (`id` ASC) VISIBLE,
  UNIQUE INDEX `measurement_id_UNIQUE` (`measurement_id` ASC) VISIBLE,
  CONSTRAINT `measurements_files_measurements_cascade`
    FOREIGN KEY (`measurement_id`)
    REFERENCES `seddb`.`measurements` (`id`)
    ON DELETE CASCADE
    ON UPDATE NO ACTION);


CREATE TABLE `seddb`.`measurements_sets_subprojects_map` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `subproject_id` INT UNSIGNED NOT NULL,
  `measurement_set_id` INT UNSIGNED NOT NULL,
  PRIMARY KEY (`id`),
  CONSTRAINT `measurement_set_subproject_cascade`
  FOREIGN KEY (`subproject_id`)
  REFERENCES `seddb`.`projects_subprojects` (`id`)
  ON DELETE CASCADE
  ON UPDATE NO ACTION);


# Difam projects
CREATE TABLE IF NOT EXISTS `seddb`.`difam_projects` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(255) NULL DEFAULT 'Unnamed project',
  `individual_archetype_id` INT UNSIGNED NULL DEFAULT NULL,
  `owner_id` INT UNSIGNED NOT NULL,
  `datetime_created` DATETIME(3) NOT NULL DEFAULT NOW(3),
  PRIMARY KEY (`id`),
  UNIQUE INDEX `id_UNIQUE` (`id` ASC) VISIBLE);


# Stored procedure for getting a measurement set
DROP procedure IF EXISTS `get_measurements_set`;
DELIMITER $$
CREATE PROCEDURE `get_measurements_set` (IN set_id INT)
BEGIN
	SELECT *
    FROM measurements_sets
    WHERE id = set_id;

	SELECT *, (SELECT COUNT(*) FROM `measurements_results_data` WHERE `measurements_results_data`.`measurement_id` = `measurements`.`id`) as data_count
	FROM measurements
	WHERE measurement_set_id = set_id;
END$$
DELIMITER ;

# Stored procedure for getting measurements belonging to a subproject
DROP procedure IF EXISTS `get_measurements_sets_in_subproject`;
DELIMITER $$
CREATE PROCEDURE `get_measurements_sets_in_subproject` (IN subproject_id INT)
BEGIN
	SELECT
		*,
        (SELECT COUNT(*) FROM `measurements` WHERE `measurements`.`measurement_set_id` = `measurements_sets`.`id`) as measurement_count
	FROM `measurements_sets`
	WHERE `measurements_sets`.`id` in
		(SELECT `measurements_sets_subprojects_map`.`measurement_set_id` FROM `measurements_sets_subprojects_map` WHERE `measurements_sets_subprojects_map`.`subproject_id` = subproject_id)
	;
END$$
DELIMITER ;
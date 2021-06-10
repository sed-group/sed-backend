# Create schema
CREATE SCHEMA IF NOT EXISTS `seddb` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;

USE seddb;

# Create user with read write access

CREATE USER IF NOT EXISTS 'rw' IDENTIFIED BY 'DONT_USE_IN_PRODUCTION!';
GRANT SELECT, INSERT, UPDATE, DELETE ON * TO 'rw';

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
  `project_id` INT UNSIGNED NOT NULL,
  `native_project_id` INT UNSIGNED NOT NULL,
  PRIMARY KEY (`id`),
  INDEX `NATIVE_SUBPROJ_ID` (`native_project_id` ASC) INVISIBLE,
  INDEX `projects_cascade_idx` (`project_id` ASC) VISIBLE,
  CONSTRAINT `projects_cascade`
    FOREIGN KEY (`project_id`)
    REFERENCES `seddb`.`projects` (`id`)
    ON DELETE CASCADE
    ON UPDATE NO ACTION);

# Create individuals table
CREATE TABLE IF NOT EXISTS `seddb`.`individuals` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(255) NOT NULL DEFAULT 'Unnamed individuals',
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

# Create individuals archetypes table
CREATE TABLE IF NOT EXISTS `seddb`.`individuals_archetypes` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(255) NOT NULL DEFAULT 'Unnamed individual archetype',
  PRIMARY KEY (`id`),
  UNIQUE INDEX `id_UNIQUE` (`id` ASC) VISIBLE);

# Create individual to archetypes map
CREATE TABLE IF NOT EXISTS `seddb`.`individuals_archetypes_map` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `individual_archetype_id` INT UNSIGNED NOT NULL,
  `individual_id` INT UNSIGNED NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `id_UNIQUE` (`id` ASC) VISIBLE,
  INDEX `individual_cascade_idx` (`individual_id` ASC) VISIBLE,
  INDEX `archetype_cascade_idx` (`individual_archetype_id` ASC) VISIBLE,
  CONSTRAINT `individual_cascade`
    FOREIGN KEY (`individual_id`)
    REFERENCES `seddb`.`individuals` (`id`)
    ON DELETE CASCADE
    ON UPDATE NO ACTION,
  CONSTRAINT `archetype_cascade`
    FOREIGN KEY (`individual_archetype_id`)
    REFERENCES `seddb`.`individuals_archetypes` (`id`)
    ON DELETE CASCADE
    ON UPDATE NO ACTION);


# Archetype parameters table
CREATE TABLE IF NOT EXISTS `seddb`.`individuals_archetypes_parameters` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `individual_archetype_id` INT UNSIGNED NOT NULL,
  `name` VARCHAR(255) NOT NULL,
  `type` TINYINT UNSIGNED NOT NULL,
  `default_value` VARCHAR(255) NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `id_UNIQUE` (`id` ASC) VISIBLE,
  INDEX `archetype_cascade_idx` (`individual_archetype_id` ASC) VISIBLE,
  CONSTRAINT `archetype_parameter_cascade`
    FOREIGN KEY (`individual_archetype_id`)
    REFERENCES `seddb`.`individuals_archetypes` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION);


# Measurements table
CREATE TABLE IF NOT EXISTS `seddb`.`measurements` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(255) NOT NULL DEFAULT 'Unnamed measurement',
  `type` TINYINT UNSIGNED NOT NULL,
  `description` TEXT NULL,
  `measurement_set_id` TINYINT UNSIGNED NOT NULL,
  PRIMARY KEY (`id`));


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
    ON DELETE NO ACTION
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
    ON DELETE NO ACTION
    ON UPDATE NO ACTION);

CREATE TABLE IF NOT EXISTS `seddb`.`measurements_sets` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(255) NOT NULL DEFAULT 'Unnamed measurement set',
  `type` TINYINT UNSIGNED NOT NULL DEFAULT 0,
  `description` TEXT NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `id_UNIQUE` (`id` ASC) VISIBLE);


# Difam projects
CREATE TABLE IF NOT EXISTS `seddb`.`difam_projects` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(255) NULL DEFAULT 'Unnamed project',
  `individual_archetype_id` INT UNSIGNED NULL DEFAULT NULL,
  `owner_id` INT UNSIGNED NOT NULL,
  `datetime_created` DATETIME(3) NOT NULL DEFAULT NOW(3),
  PRIMARY KEY (`id`),
  UNIQUE INDEX `id_UNIQUE` (`id` ASC) VISIBLE);



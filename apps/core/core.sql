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

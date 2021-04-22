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

# Create default admin user
INSERT INTO `seddb`.`users` (`username`, `password`,`scopes`, `disabled`) VALUES ('admin', '$2b$12$HrAma.HCdIFuHtnbVcle/efa9luh.XUqZapqFEUISj91TKTN6UgR6', 'admin', False);

# User table index for alphabetic order
# TODO: Index users

# Create applications table
CREATE TABLE IF NOT EXISTS `seddb`.`applications` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(255) NOT NULL,
  `description` VARCHAR(1000) NULL DEFAULT NULL,
  `contact` VARCHAR(255) NULL DEFAULT NULL,
  `href` VARCHAR(500) NULL COMMENT 'project homepage',
  `href_access` VARCHAR(500) NOT NULL COMMENT 'frontend url',
  `href_docs` VARCHAR(500) NULL DEFAULT NULL COMMENT 'url for documentation',
  `href_source` VARCHAR(500) NULL DEFAULT NULL,
  `href_api` VARCHAR(500) NULL DEFAULT NULL COMMENT 'url for api root endpoint',
  PRIMARY KEY (`id`),
  UNIQUE INDEX `id_UNIQUE` (`id` ASC) VISIBLE,
  UNIQUE INDEX `name_UNIQUE` (`name` ASC) VISIBLE,
  UNIQUE INDEX `href_access_UNIQUE` (`href_access` ASC) VISIBLE);

# Create projects table
CREATE TABLE IF NOT EXISTS `seddb`.`projects` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(255) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `id_UNIQUE` (`id` ASC) VISIBLE);


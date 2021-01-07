# Create schema
CREATE SCHEMA `seddb` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;

USE seddb

# Create user with read write access
CREATE USER 'rw' IDENTIFIED BY 'DONT_USE_IN_PRODUCTION!';
GRANT SELECT, INSERT, UPDATE, DELETE ON * TO 'rw';

# Create users TABLE
CREATE TABLE `seddb`.`users` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `username` VARCHAR(45) NOT NULL,
  `password` VARCHAR(100) NOT NULL,
  `email` VARCHAR(100) NULL,
  `full_name` VARCHAR(255) NULL,
  `scopes` VARCHAR(500) NULL DEFAULT '';
  `disabled` TINYINT(1) UNSIGNED NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `id_UNIQUE` (`id` ASC) VISIBLE,
  UNIQUE INDEX `username_UNIQUE` (`username` ASC) VISIBLE);

# User table index for alphabetic order


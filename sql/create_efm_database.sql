# Create schema
CREATE SCHEMA IF NOT EXISTS `seddb` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;


USE seddb;


# Create tree TABLE
CREATE TABLE IF NOT EXISTS `seddb`.`efm_trees` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `top_level_ds_id` INT UNSIGNED NULL,
  `name` VARCHAR(255) NOT NULL,
  `description` VARCHAR(5000) NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `id_UNIQUE` (`id` ASC) VISIBLE);

CREATE TABLE IF NOT EXISTS `seddb`.`efm_designsolutions` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `tree_id` INT UNSIGNED NOT NULL,
  `name` VARCHAR(255) NOT NULL,
  `description` VARCHAR(5000) NULL,
  `is_top_level_ds` TINYINT NOT NULL DEFAULT 0,
  `isb_id` INT UNSIGNED NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `id_UNIQUE` (`id` ASC) VISIBLE,
  CONSTRAINT `tree_ds_cascade`
    FOREIGN KEY (`tree_id`)
    REFERENCES `seddb`.`efm_trees` (`id`)
    ON DELETE CASCADE
    ON UPDATE NO ACTION);

CREATE TABLE IF NOT EXISTS `seddb`.`efm_functionalrequirements` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `tree_id` INT UNSIGNED NOT NULL,
  `name` VARCHAR(255) NOT NULL,
  `description` VARCHAR(5000) NULL,
  `rf_id` INT UNSIGNED NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `id_UNIQUE` (`id` ASC) VISIBLE,
  CONSTRAINT `tree_fr_cascade`
    FOREIGN KEY (`tree_id`)
    REFERENCES `seddb`.`efm_trees` (`id`)
    ON DELETE CASCADE
    ON UPDATE NO ACTION,
  CONSTRAINT `ds_fr_cascade`
    FOREIGN KEY (`rf_id`)
    REFERENCES `seddb`.`efm_designsolutions` (`id`)
    ON DELETE CASCADE
    ON UPDATE NO ACTION);
  
CREATE TABLE IF NOT EXISTS `seddb`.`efm_interactswith` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `tree_id` INT UNSIGNED NOT NULL,
  `iw_type` VARCHAR(10) NOT NULL,
  `description` VARCHAR(5000) NULL,
  `to_ds_id` INT UNSIGNED NULL,
  `from_ds_id` INT UNSIGNED NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `id_UNIQUE` (`id` ASC) VISIBLE,
  CONSTRAINT `tree_iw_cascade`
    FOREIGN KEY (`tree_id`)
    REFERENCES `seddb`.`efm_trees` (`id`)
    ON DELETE CASCADE
    ON UPDATE NO ACTION,
  CONSTRAINT `to_ds_cascade`
    FOREIGN KEY (`to_ds_id`)
    REFERENCES `seddb`.`efm_designsolutions` (`id`)
    ON DELETE CASCADE
    ON UPDATE NO ACTION,
  CONSTRAINT `from_ds_cascade`
    FOREIGN KEY (`from_ds_id`)
    REFERENCES `seddb`.`efm_designsolutions` (`id`)
    ON DELETE CASCADE
    ON UPDATE NO ACTION);


CREATE TABLE IF NOT EXISTS `seddb`.`efm_constraints` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `tree_id` INT UNSIGNED NOT NULL,
  `name` VARCHAR(255) NOT NULL,
  `description` VARCHAR(5000) NULL,
  `icb_id` INT UNSIGNED NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `id_UNIQUE` (`id` ASC) VISIBLE,
  CONSTRAINT `tree_c_cascade`
    FOREIGN KEY (`tree_id`)
    REFERENCES `seddb`.`efm_trees` (`id`)
    ON DELETE CASCADE
    ON UPDATE NO ACTION,
  CONSTRAINT `icb_cascade`
    FOREIGN KEY (`icb_id`)
    REFERENCES `seddb`.`efm_designsolutions` (`id`)
    ON DELETE CASCADE
    ON UPDATE NO ACTION);

CREATE TABLE IF NOT EXISTS `seddb`.`efm_concepts` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `tree_id` INT UNSIGNED NOT NULL,
  `name` VARCHAR(255) NOT NULL,
  `dna` VARCHAR(5000) NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `id_UNIQUE` (`id` ASC) VISIBLE,
  CONSTRAINT `tree_co_cascade`
    FOREIGN KEY (`tree_id`)
    REFERENCES `seddb`.`efm_trees` (`id`)
    ON DELETE CASCADE
    ON UPDATE NO ACTION);

ALTER TABLE `efm_designsolutions`
  ADD
    CONSTRAINT `fr_ds_cascade`
    FOREIGN KEY (`isb_id`)
    REFERENCES `seddb`.`efm_functionalrequirements` (`id`)
    ON DELETE CASCADE
    ON UPDATE NO ACTION

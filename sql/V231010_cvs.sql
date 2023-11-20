ALTER TABLE `seddb`.`cvs_vd_design_values`
  MODIFY COLUMN `value` CHAR(255);

ALTER TABLE `seddb`.`cvs_design_mi_formulas`
  ADD COLUMN `time_latex` TEXT NULL AFTER `time`,
  ADD COLUMN `cost_latex` TEXT NULL AFTER `cost`,
  ADD COLUMN `revenue_latex` TEXT NULL AFTER `revenue`;
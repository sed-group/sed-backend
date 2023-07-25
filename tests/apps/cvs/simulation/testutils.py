from typing import Tuple, List
from sedbackend.apps.cvs.design.models import Design, DesignGroup
from sedbackend.apps.cvs.project.models import CVSProject
from sedbackend.apps.cvs.simulation.models import SimSettings
from sedbackend.apps.cvs.vcs.models import VCS
import tests.apps.cvs.testutils as tu


def setup_single_simulation(user_id) -> Tuple[CVSProject, VCS, DesignGroup, List[Design], SimSettings]:
  project = tu.seed_random_project(user_id)
  vcs = tu.seed_random_vcs(project.id, current_user.id)
  design_group = tu.seed_random_design_group(project.id)
  tu.seed_random_formulas(project.id, vcs.id, design_group.id, user_id, 15) #Also creates the vcs rows
  design = tu.seed_random_designs(project.id, design_group.id, 1)

  settings = tu.seed_simulation_settings(project.id, [vcs.id], [design[0].id])

  return project, vcs, design_group, design, settings

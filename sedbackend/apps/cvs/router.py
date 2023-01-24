from fastapi import APIRouter, Security

from sedbackend.apps.core.authentication.utils import verify_token

from sedbackend.apps.cvs.project.router import router as router_project
from sedbackend.apps.cvs.vcs.router import router as router_vcs
from sedbackend.apps.cvs.design.router import router as router_design
from sedbackend.apps.cvs.market_input.router import router as router_market_input
from sedbackend.apps.cvs.life_cycle.router import router as router_life_cycle
from sedbackend.apps.cvs.simulation.router import router as router_simulation
from sedbackend.apps.cvs.link_design_lifecycle.router import router as router_link_design_lifecycle
from sedbackend.apps.cvs.distributions.router import router as router_distributions

router = APIRouter()

router.include_router(router_project, tags=['cvs'], dependencies=[Security(verify_token)])
router.include_router(router_vcs, tags=['cvs'], dependencies=[Security(verify_token)])
router.include_router(router_design, tags=['cvs'], dependencies=[Security(verify_token)])
router.include_router(router_life_cycle, tags=['cvs'], dependencies=[Security(verify_token)])
router.include_router(router_link_design_lifecycle, tags=['cvs'], dependencies=[Security(verify_token)])
router.include_router(router_market_input, tags=['cvs'], dependencies=[Security(verify_token)])
router.include_router(router_simulation, tags=['cvs'], dependencies=[Security(verify_token)])
router.include_router(router_distributions, tags=['cvs'], dependencies=[Security(verify_token)])

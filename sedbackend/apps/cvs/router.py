from fastapi import APIRouter, Security

from sedbackend.apps.core.authentication.utils import verify_token

from sedbackend.apps.cvs.project.router import router as router_project
from sedbackend.apps.cvs.vcs.router import router as router_vcs
from sedbackend.apps.cvs.design.router import router as router_design
from sedbackend.apps.cvs.market_input.router import router as router_market_input
from sedbackend.apps.cvs.life_cycle.router import router as router_life_cycle
from sedbackend.apps.cvs.simulation.router import router as router_simulation

router = APIRouter()

CVS_APP_SID = 'MOD.CVS'

router.include_router(router_project, prefix='/project', tags=['cvs project'], dependencies=[Security(verify_token)])
router.include_router(router_vcs, prefix='/vcs', tags=['cvs vcs'], dependencies=[Security(verify_token)])
router.include_router(router_design, prefix='/design', tags=['cvs design'], dependencies=[Security(verify_token)])
router.include_router(router_life_cycle, prefix='/life_cycle', tags=['cvs life cycle'], dependencies=[Security(verify_token)])
router.include_router(router_market_input, prefix='/market_input', tags=['cvs market input'], dependencies=[Security(verify_token)])
router.include_router(router_simulation, prefix='/simulation', tags=['cvs simulation'], dependencies=[Security(verify_token)])



from fastapi import APIRouter

from sedbackend.apps.cvs.distributions import models, implementation
router = APIRouter()


@router.post(
    '/distribution/uniform',
    summary='Creates a uniform distribution',
    response_model=models.Distribution,
)
def uniform_distribution(center: float, x_range: float, n_samples: int) -> models.Distribution:
    return implementation.uniform_distribution(center, x_range, n_samples)


@router.post(
    '/distribution/gaussian',
    summary='Creates a gaussian distribution',
    response_model=models.Distribution,
)
def gaussian_distribution(mu: float, sigma: float, n_samples: int) -> models.Distribution:
    return implementation.gaussian_distribution(mu, sigma, n_samples)

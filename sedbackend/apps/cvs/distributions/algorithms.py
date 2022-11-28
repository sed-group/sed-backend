import numpy as np
from mvm import UniformFunc, GaussianFunc
from sedbackend.apps.cvs.distributions import models


# Simple 1-dimensional uniform distribution
def uniform_distribution(center: float, x_range: float, n_samples: int) -> models.Distribution:
    dist = UniformFunc(center=np.array([center]), interval=np.array([[x_range, ]]))
    dist.random(n_samples)  # draw n samples from the distribution (they are stores inside)

    mean = dist.samples.mean()  # should be close to center
    std = dist.samples.std()

    # true standard deviation
    exact_std = np.sqrt(((x_range * 2) ** 2) / 12)

    return models.Distribution(
        approx_mean=mean,
        exact_mean=center,
        approx_std=std,
        exact_std=exact_std
    )


# Simple 1-dimensional Gaussian distribution
def gaussian_distribution(mu: float, sigma: float, n_samples: int) -> models.Distribution:

    dist = GaussianFunc(mu=np.array([mu]), sigma=np.array([[sigma ** 2, ]]))
    dist.random(n_samples)  # draw n samples from the distribution (they are stores inside)

    mean = dist.samples.mean()  # should be close to mu
    std = dist.samples.std()

    return models.Distribution(
        approx_mean=mean,
        exact_mean=mu,
        approx_std=std,
        exact_std=sigma
    )

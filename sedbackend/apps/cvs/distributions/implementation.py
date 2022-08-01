from sedbackend.apps.cvs.distributions import models, algorithms


# Simple 1-dimensional uniform distribution
def uniform_distribution(center: float, range: float, n_samples: int) -> models.Distribution:
    return algorithms.uniform_distribution(center, range, n_samples)


# Simple 1-dimensional Gaussian distribution
def gaussian_distribution(mu: float, sigma: float, n_samples: int) -> models.Distribution:
    return algorithms.gaussian_distribution(mu, sigma, n_samples)

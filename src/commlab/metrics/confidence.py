import math


def wilson_interval(errors: int, trials: int, z: float = 1.959963984540054) -> tuple[float, float]:
    """Wilson score interval for a Bernoulli error probability."""
    e = int(errors); n = int(trials)
    if n <= 0 or e < 0 or e > n:
        raise ValueError("require 0 <= errors <= trials and trials > 0")
    phat = e / n
    z2 = z*z
    denom = 1.0 + z2/n
    center = (phat + z2/(2*n))/denom
    radius = z*math.sqrt(phat*(1-phat)/n + z2/(4*n*n))/denom
    return max(0.0, center-radius), min(1.0, center+radius)


def ber_with_wilson(errors: int, bits: int, z: float = 1.959963984540054) -> tuple[float, float, float]:
    lo,hi=wilson_interval(errors,bits,z)
    return errors/bits,lo,hi

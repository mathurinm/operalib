"""OVK learning, unit tests.

The :mod:`sklearn.tests.test_QuantileRegression` tests OVK quantile regression
estimator.
"""

import operalib as ovk

from sklearn.utils.estimator_checks import check_estimator
import numpy as np
from scipy.stats import norm
from distutils.version import LooseVersion
from warnings import warn


def toy_data(n=50, probs=[0.5], noise=1.):
    """Sine wave toy dataset.

    Parameters
    ----------
    n : {integer}
        Number of samples to generate.

    probs : {list}, shape = [n_quantiles]
        Probabilities (quantiles levels).

    Returns
    -------
    X : {array}, shape = [n]
        Input data.

    y : {array}, shape = [n]
        Targets.

    quantiles : {array}, shape = [n x n_quantiles]
        True conditional quantiles.
    """
    t_min, t_max = 0., 1.5  # Bounds for the input data
    t_down, t_up = 0., 1.5  # Bounds for the noise
    t = np.random.rand(n) * (t_max - t_min) + t_min
    t = np.sort(t)
    pattern = -np.sin(2. * np.pi * t)  # Pattern of the signal
    enveloppe = 1. + np.sin(2 * np.pi * t / 3.)  # Enveloppe of the signal
    pattern = pattern * enveloppe
    # Noise decreasing std (from noise+0.2 to 0.2)
    noise_std = 0.2 + noise * (t_up - t) / (t_up - t_down)
    # Gaussian noise with decreasing std
    add_noise = noise_std * np.random.randn(n)
    observations = pattern + add_noise
    quantiles = [pattern + np.asarray([norm.ppf(p, loc=0., scale=abs(noise_i))
                                       for noise_i in noise_std]) for p in
                 probs]
    return t[:, None], observations, quantiles


def test_valid_estimator():
    """Test whether ovk.Quantile is a valid sklearn estimator."""
    from sklearn import __version__
    # Adding patch revision number cause crash
    if LooseVersion(__version__) >= LooseVersion('0.18'):
        check_estimator(ovk.Quantile)
    else:
        warn('sklearn\'s check_estimator seems to be broken in __version__ <='
             ' 0.17.x... skipping')


def test_learn_quantile():
    """Test OVK quantile estimator fit, predict."""
    probs = np.linspace(0.1, 0.9, 5)  # Quantile levels of interest
    x_train, y_train, z_train = toy_data(50)
    x_test, y_test, z_test = toy_data(1000, probs=probs)

    # Joint quantile regression
    lbda = 1e-2
    gamma = 1e1
    joint = ovk.Quantile(probs=probs, kernel='DGauss', lbda=lbda,
                         gamma=gamma, gamma_quantile=1e-2)
    # Independent quantile regression
    ind = ovk.Quantile(probs=probs, kernel='DGauss', lbda=lbda,
                       gamma=gamma, gamma_quantile=np.inf)
    # Independent quantile regression (with non-crossing constraints)
    nc = ovk.Quantile(probs=probs, kernel='DGauss', lbda=lbda,
                      gamma=gamma, gamma_quantile=np.inf, nc_const=True)

    # Fit on training data
    for reg in [joint, ind, nc]:
        reg.fit(x_train, y_train)
        assert reg.score(x_test, y_test) > 0.7

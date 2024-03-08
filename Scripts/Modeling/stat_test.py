import itertools as it
from typing import List
import numpy as np
import pandas as pd
import scipy.stats as ss

from scipy.stats import wilcoxon

def VD_A(treatment: List[float], control: List[float]):
    """
    Computes Vargha and Delaney A index
    A. Vargha and H. D. Delaney.
    A critique and improvement of the CL common language
    effect size statistics of McGraw and Wong.
    Journal of Educational and Behavioral Statistics, 25(2):101-132, 2000

    The formula to compute A has been transformed to minimize accuracy errors
    See: http://mtorchiano.wordpress.com/2014/05/19/effect-size-of-r-precision/

    :param treatment: a numeric list
    :param control: another numeric list

    :returns the value estimate and the magnitude
    """
    m = len(treatment)
    n = len(control)

    if m != n:
        raise ValueError("Data d and f must have the same length")

    r = ss.rankdata(treatment + control)
    r1 = sum(r[0:m])

    # Compute the measure
    # A = (r1/m - (m+1)/2)/n # formula (14) in Vargha and Delaney, 2000
    A = (2 * r1 - m * (m + 1)) / (2 * n * m)  # equivalent formula to avoid accuracy errors

    return A

def wilcoxon_test(x: List[float], y: List[float]):
    """
    Computes wilcoxon test
    :param treatment: a numeric list
    :param control: another numeric list

    :returns the value estimate and the magnitude
    """

    stat, p = wilcoxon(x, y, alternative='less')
    # Sig. codes: < 0.001 (***) 0.01 (**) 0.05 (*) 0.1 (.) 1 ( )
    sig_code = '' if p > 0.1 else '.' if p > 0.05 else '*' if p > 0.01 else '**' if p > 0.001 else '***'
    sig = 'Yes' if p <= 0.05 else 'No'
    return p, sig_code, sig

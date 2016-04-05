#!/usr//bin/env python
# -*- coding: utf-8; mode: python; -*-

"""Module providing common heano utils.

Attributes:
floatX (method): force float type expected by theano
rmsprop (method): separate training set into explicit and implicit instances

"""

##################################################################
# Imports
from __future__ import absolute_import, print_function

from theano import config, tensor as TT
import numpy as np
import theano


##################################################################
# Methods
def floatX(a_data, a_dtype=config.floatX):
    """Return numpy array populated with the given data.

    Args:
    data (np.array):
      input tensor
    dtype (class):
      digit type

    Returns:
    (np.array):
     array populated with the given data

    """
    return np.asarray(a_data, dtype=a_dtype)


def rmsprop(tparams, grads, x, y, cost):
    """
    A variant of  SGD that scales the step size by running average of the
    recent step norms.

    Parameters:
    tpramas (Theano SharedVariable):
        Model parameters
    grads (Theano variable):
        Gradients of cost w.r.t to parameres
    x (Theano variable):
        Model inputs
    y (Theano variable):
        Targets
    cost (Theano variable):
        Objective fucntion to minimize

    Notes:
    For more information, see [Hint2014]_.

    .. [Hint2014] Geoff Hinton, *Neural Networks for Machine Learning*,
       lecture 6a,
       http://cs.toronto.edu/~tijmen/csc321/slides/lecture_slides_lec6.pdf

    """
    zipped_grads = [theano.shared(p.get_value() * floatX(0.))
                    for p in tparams]
    running_grads = [theano.shared(p.get_value() * floatX(0.))
                     for p in tparams]
    running_grads2 = [theano.shared(p.get_value() * floatX(0.))
                      for p in tparams]

    zgup = [(zg, g) for zg, g in zip(zipped_grads, grads)]
    rgup = [(rg, 0.95 * rg + 0.05 * g) for rg, g in zip(running_grads, grads)]
    rg2up = [(rg2, 0.95 * rg2 + 0.05 * (g ** 2))
             for rg2, g in zip(running_grads2, grads)]

    f_grad_shared = theano.function([x, y], cost,
                                    updates=zgup + rgup + rg2up,
                                    name='rmsprop_f_grad_shared')

    updir = [theano.shared(p.get_value() * floatX(0.))
             for p in tparams]
    updir_new = [(ud, 0.9 * ud - 1e-4 * zg / TT.sqrt(rg2 - rg ** 2 + 1e-4))
                 for ud, zg, rg, rg2 in zip(updir, zipped_grads, running_grads,
                                            running_grads2)]
    param_up = [(p, p + udn[1])
                for p, udn in zip(tparams, updir_new)]
    f_update = theano.function([], [], updates=updir_new + param_up,
                               on_unused_input='ignore',
                               name='rmsprop_f_update')
    return (f_grad_shared, f_update, (zipped_grads, running_grads,
                                      running_grads2, updir))
from __future__ import division
import numpy.ma as ma
import numpy as np
import scipy as s
import math

from biofam.core.utils import dotd
from biofam.core import gpu_utils

# Import manually defined functions
from .variational_nodes import Constant_Variational_Node

class Y_Node(Constant_Variational_Node):
    def __init__(self, dim, value):
        Constant_Variational_Node.__init__(self, dim, value)

        # Mask missing values
        self.mask = self.mask()

        self.mini_batch = None
        self.mini_mask = None

    def precompute(self, options=None):
        """ Method to precompute some terms to speed up the calculations """

        # Dimensionalities
        self.N = self.dim[0] - self.getMask().sum(axis=0)
        self.D = self.dim[1] - self.getMask().sum(axis=1)

        # GPU mode
        gpu_utils.gpu_mode = options['gpu_mode']

        # Constant ELBO terms
        self.likconst = -0.5 * s.sum(self.N) * s.log(2.*s.pi)

    def mask(self):
        """ Method to mask missing observations """
        mask = s.isnan(self.value)
        self.value[mask] = 0.
        return mask

    def getMask(self):
        """ Get method for the mask """
        if self.mini_batch is None:
            return self.mask
        else:
            return self.mini_mask
            
    def define_mini_batch(self, ix):
        """ Method to define a mini-batch (only for stochastic inference) """
        self.mini_batch = self.value[ix,:]
        self.mini_mask = self.mask[ix,:]

    def get_mini_batch(self):
        """ Method to retrieve a mini-batch (only for stochastic inference) """
        if self.mini_batch is None:
            return self.getExpectation()
        else:
            return self.mini_batch

    def calculateELBO(self, TauTrick=False):
        """ Method to calculate evidence lower bound """


        if TauTrick: # Important: this assumes that the Tau update has been done prior to calculating elbo of Y
            tauQ_param = self.markov_blanket["Tau"].getParameters("Q")
            tauP_param = self.markov_blanket["Tau"].getParameters("P")

            Tau = self.markov_blanket["Tau"].getExpectations()
            Tau["lnE"][mask] = 0.
            Tau["E"][mask] = 0.

            # TO-DO: TAKE INTO ACCOUNT GROUPS
            # TO-DO: CHECK MISSING VALUES IN TAU["E"]
            elbo = self.likconst + 0.5*s.sum(Tau["lnE"]) - s.dot(Tau["E"],tauQ_param["b"] - tauP_param["b"])

        else:
            # Collect expectations from nodes
            Y = self.getExpectation()
            Tau = self.markov_blanket["Tau"].getExpectations(expand=False)
            mask = self.getMask()
            Wtmp = self.markov_blanket["W"].getExpectations()
            Ztmp = self.markov_blanket["Z"].getExpectations()
            W, WW = Wtmp["E"].T, Wtmp["E2"].T
            Z, ZZ = Ztmp["E"], Ztmp["E2"]

            tmp = s.square(Y) \
                + ZZ.dot(WW) \
                - s.dot(s.square(Z),s.square(W)) + s.square(Z.dot(W)) \
                - 2*Z.dot(W)*Y 
            tmp *= 0.5
            tmp[mask] = 0.
            
            elbo = self.likconst
            groups = self.markov_blanket["Tau"].groups
            for g in range(len(np.unique(groups))):
                idx = groups==g
                foo = (~mask[idx,:]).sum(axis=0)
                elbo += 0.5*(Tau["lnE"][g,:]*foo).sum() - (Tau["E"][g,:]*tmp[idx,:]).sum()

        return elbo


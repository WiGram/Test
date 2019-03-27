"""
Date:    February 2nd, 2019
Authors: Kristian Strand and William Gram
Subject: Choosing optimal portfolio weights

Description:
This script takes a CRRA utility function and
outputs expected utility.
"""

import numpy as np
from numba import jit
np.set_printoptions(suppress = True)   # Disable scientific notation


@jit(nopython = True)
def expectedUtility(M,N,W,T,rf,R,wM,G,ApB):
    """
    Produces
    ---------------------------------------------
    Vector of expected utilities for each possible
    portfolio allocation determined by the amount
    of sets of weights simulated (W).
    
    Inputs
    ---------------------------------------------
    M:    Scalar indicating how many state paths are simulated
    N:    Scalar indicating how many sets of return paths are simulated
    W:    Scalar indicating how many portfolio allocations are possible
    T:    Scalar indicating how many periods have been simulated
    rf:   Scalar for risk-free rate
    R:    (M*N x (A x T)) matrix of M*N simulated returns for A assets of T periods
    wM:   (A x W) matrix of normalised weights
    G:    Scalar GAMMA indicating degree of risk aversion
    ApB:  Scalar (A+1) indicating amount of risky assets plus rf bank account
    
    Returns
    ---------------------------------------------
    eU:       (Wx1) Vector of expected utility values
    uMax:     Scalar of the maximal expected utility
    uArgMax:  Scalar of the index of the maximal expected utility
    wMax:     Vector of weights that provide maximal expected utility
    """
    
    # Initialise empty matrix of expected utility
    eU = np.zeros((W, M * N))
    
    # Precompute risk aversion parameter
    RA = 1 - G
    
    # Convert returns to decimal representation
    R  = R / 100.0
    rf = rf / 100.0
    
    # Compute weighted cumulated return from risk-free asset (Scalar)
    cRF = wM[ApB-1,:] * np.exp(T * rf)
    """
    (1) Returns are compounded across time - sum must be along columns: axis = 1
    (2) We are testing all W different portfolio weights
    """
    for w in range(W):
        
        # Print iteration to show progress
        # print(w)
        for n in range(M * N):
            
            # Compute weighted cumulated return from risky assets
            cRR = wM[:ApB-1,w] * np.exp(np.sum(rf + R[n]))
            
            # Compute expected utility at each portfolio allocation
            eU[w,n]   = (cRF[w] + np.sum(cRR) ) ** RA / RA
    
    eU = np.sum(eU, axis = 1) / (M * N)
    
    uMax = np.max(eU)
    uArgMax = np.argmax(eU)
    wMax = wM[:,uArgMax]
    
    return eU, uMax, uArgMax, wMax

"""
# Test the function by running the below code
# -----------------------------------------------
from pfWeightsModule import pfWeights
import simulateSimsReturns as ssr

# -----------------------
# TO RUN ssr.returnSim
S = 3
A = 5
M = 100
T = 1
G = 5
start = 1
mu = np.random.normal(size = (A,S))
cov = np.array([np.cov(np.random.normal(size = (5,100))) for i in range(S)])
probs = np.array([[0.77, 0.56, 0.05],
                  [0.16, 0.88, 0.09],
                  [0.07, 0.06, 0.86]])

# ----------------------

# ----------------------
# TO RUN pfWeights:
A = A
ApB = A + 1
W = 1000
----------------------

M = M
N = 1
W = W
T = T
rf = 0.19
np.random.seed(12345)
u = np.random.uniform(0,1,(M,T))
R, states = ssr.returnSim(S, M, N, A, start, mu, cov, probs, T, u)

weights = np.random.random(size = (ApB, W))
wM = pfWeights(weights)

eU, uMax, uArgMax, wMax = expectedUtility(M,N,W,T,rf,R,wM,G,ApB)
wMax

"""
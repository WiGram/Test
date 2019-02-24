# -*- coding: utf-8 -*-
"""
Date:    February 20th, 2019
Authors: Kristian Strand and William Gram
Subject: Parameter estimation using the bootstrap method

Description:
Applying the bootstrap method from page 58 of Hidden Markov
Models for Time Series - an introduction using R by Zucchini,
MacDonald and Langrock.
"""

import genData as gd
import MSreturnSim as rs
from matplotlib import pyplot as plt
import plotsModule as pltm
import EM_NM_EX as em
import numpy as np
import pandas as pd

prices, monthlyRets, excessMRets, colNames, assets, monthlyVol, retCov, rf, pDates, rDates = gd.genData()

# ============================================= #
# ===== Idiosyncratic removal ================= #
# ============================================= #

"""
# ===== Monthly Absolute ===== #
# monthlyRets = monthlyRets.drop(['S&P 500', 'Gov'], axis = 1)
monthlyRets = monthlyRets.drop(['S&P 500'], axis = 1)
colNames = monthlyRets.columns
assets = len(colNames)
returns = np.array(monthlyRets.T)
"""

# ===== Monthly excess returns ===== #
# monthlyRets = monthlyRets.drop(['S&P 500', 'Gov'], axis = 1)
excessMRets = excessMRets.drop(['S&P 500'], axis = 1)
colNames = excessMRets.columns
assets = len(colNames)
returns = np.array(excessMRets.T)

# ============================================= #
# ===== Parameter initialisation ============== #
# ============================================= #

emSims = 250 # [EM]-algorithm simulations
bsSims = 100  # [b]ootstrap[S]ims
states = 3
mat    = len(returns[0,:])
probs  = np.repeat(1.0 / states, states * states).reshape(states, states)

m   = np.zeros((bsSims, assets, states))
v   = np.zeros((bsSims, states, assets, assets))
p   = np.zeros((bsSims, states, states))
l   = np.zeros((bsSims))
pSt = np.zeros((bsSims, states, mat))
pSt[0] = np.random.uniform(size = states * mat).reshape(states, mat)

ms, vs, ps, llh, pStar, pStarT = em.EM(returns, emSims, mat, states, assets, probs, pSt[0])

m[0]   = ms[emSims - 1]
v[0]   = vs[emSims - 1]
p[0]   = ps[emSims - 1]
l[0]   = llh[emSims - 1]
startReg = np.argmax(pStar[:,0]) + 1 #technicality due to indexing.

u = np.random.uniform(0, 1, size = bsSims * mat).reshape(bsSims, mat)

for r in range(1,bsSims):
    simReturns = rs.returnSim3(states, assets, startReg, m[0], v[0], p[0], mat, u[r,:])

    ms, vs, ps, llh, pStar, pStarT = em.EM(simReturns, emSims, mat, states, assets, probs, pSt[0])

    m[r]   = ms[emSims - 1]
    v[r]   = vs[emSims - 1]
    p[r]   = ps[emSims - 1]
    l[r]   = llh[emSims - 1]
    pSt[r] = pStar

stateTitle = ['State '+i for i in map(str,range(1, states + 1))]
volTitle   = ['Volatility, state ' + i for i in map(str, range(1, states + 1))]
retTitle   = ['Return, state ' + i for i in map(str, range(1, states + 1))]

# Log-likelihood convergence plot
pltm.plotUno(range(bsSims), l, yLab = 'log-likelihood value')

# Plot stay probabilities for each regime 1,2,...,S
idx  = np.zeros((bsSims, states)).astype(int)
for i in range(bsSims):
    idx[i,0]  = int(np.argmax(np.diag(p[i,:,:])))
    idx[i,2]  = int(np.argmin(np.diag(p[i,:,:])))
    idx[i,1]  = int(np.where(np.diag(p[i,:,:]) == np.median(np.diag(p[i,:,:])))[0])

# Probabilities being plotted
for i in range(states):
    plt.plot(np.diag(p[:,idx[:,i],idx[:,i]]))
plt.show()


# Compare idx derived from returns to those achieved from probs
jdx  = np.zeros((bsSims, states)).astype(int)
for i in range(bsSims):
    jdx[i,0]  = int(np.argmax(m[i,0,:]))
    jdx[i,2]  = int(np.argmin(m[i,0,:]))
    jdx[i,1]  = int(np.where(m[i,0,:] == np.median(m[i,0,:]))[0])

# Plotting of returns
newMu = np.zeros((bsSims, states))
for j in range(bsSims):
    newMu[j,:] = m[j,0,jdx[j,:]]

# WIP: plot confidence bands around e.g. mu
test  = np.zeros((bsSims,states,states))
for i in range(states):
    test[:,0,i] = np.quantile(newMu[:,i], 0.25)
    test[:,1,i] = np.mean(newMu[:,i])
    test[:,2,i] = np.quantile(newMu[:,i], 0.75)

cols  = ('b-','r-','k-')
lines = ('b--','r--','k--')

for i, c, cc in zip(range(states), cols, lines):
    plt.plot(newMu[:,i], c)
    plt.plot(test[:,0,i], cc)
    plt.plot(test[:,2,i], cc)
plt.show()

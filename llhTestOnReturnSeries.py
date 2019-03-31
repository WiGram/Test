"""
Date:    February 28th, 2019
Authors: Kristian Strand and William Gram
Subject: Parameter estimation of pseudo-residuals

Description:
ML estimation of parameters for different model
specifications of pseudo-residuals. The purpose is
to test whether the models generating the pseudo-
residuals is well-specified, which is tested through
tests on the properties of the pseudo-residuals.
"""

import genData as gd
import pandas as pd
import numpy as np
from scipy import stats
from scipy.optimize import minimize
from matplotlib import pyplot as plt
np.set_printoptions(suppress = True)   # Disable scientific notation

def testStat(lStd, lTest):
    return - 2 * (lStd - lTest)

def pValue(testStat, type = 'normal'):
    if type == 'normal':
        return ValueError('WIP')

def densityFct(z, mean, vol):
    return 1 / np.sqrt(2.0 * np.pi * vol ** 2) * np.exp(-0.5 * (z - mean)**2 / vol ** 2)

def modelStd(z):
    return - np.sum(  np.log(densityFct(z, 0.0, 1.0)))

def modelNorm(params, z):
    alpha = params[0]  # alpha
    gamma  = params[1]  # sigma
    #
    mean = alpha
    vol  = np.exp(gamma)
    #
    return - np.sum(  np.log(densityFct(z, mean, vol))  )

def modelARone(params, z):
    z_lag  = z.shift(1)[1:]
    z_lead = z[1:]
    #
    alpha = params[0]
    gamma = params[1] # sigma = exp(gamma) <= ensures sigma > 0
    arOne = params[2]
    # 
    mean = alpha + arOne * z_lag
    vol  = np.exp(gamma)
    return - np.sum(  np.log(densityFct(z_lead, mean, vol))  )

def modelARtwo(params, z):
    z_llag = z.shift(2)[2:]
    z_lag  = z.shift(1)[2:]
    z_lead = z[2:]
    # 
    alpha = params[0]
    gamma = params[1]
    arOne = params[2]
    arTwo = params[3]
    #
    mean = alpha + arOne*z_lag + arTwo*z_llag
    vol  = np.exp(gamma)
    #
    return - np.sum(  np.log(densityFct(z_lead, mean, vol))  )

def modelARtwoS(params, z):
    z_llag = z.shift(2)[2:]
    z_lag  = z.shift(1)[2:]
    z_lead = z[2:]
    # 
    alpha  = params[0]
    gamma  = params[1]
    arOne  = params[2]
    arTwo  = params[3]
    arOneS = params[4]
    arTwoS = params[5]
    #
    mean = alpha + arOne*z_lag + arTwo*z_llag + arOneS*(z_lag**2) + arTwoS*(z_llag**2)
    vol  = np.exp(gamma)
    #
    return - np.sum(  np.log( densityFct(z_lead, mean, vol) )  )

def modelX(params, z, ex):
    alpha = params[0]
    gamma = params[1]
    beta  = params[2]
    #
    mean = alpha + beta * np.array(ex)
    vol  = np.exp(gamma)
    #
    return - np.sum(  np.log(densityFct(z, mean, vol))   )

def modelARX(params, z, ex):
    z_lag  = z.shift(1)[1:]
    z_lead = z[1:]
    #
    alpha = params[0]
    gamma = params[1]
    beta  = params[2]
    arOne = params[3]
    #
    mean = alpha + beta * np.array(ex) + arOne * z_lag
    vol  = np.exp(gamma)
    #
    return - np.sum(  np.log(densityFct(z_lead, mean, vol))   )



# ============================================= #
# ===== Data load ============================= #
# ============================================= #

prices, monthlyRets, excessMRets, colNames, assets, monthlyVol, retCov, rf, pDates, rDates = gd.genData()
y = excessMRets.drop(['S&P 500'], axis = 1)
colNames = y.columns
A = len(colNames) # Assets

div  = pd.read_excel('/home/william/Dropbox/KU/K4/Python/DivYield.xlsx', 'Monthly')
div  = div.iloc[:,1]


# ============================================= #
# ===== Likelihood retributions =============== #
# ============================================= #

# Initial parameters: Values are guided by sporadic minimisation tests
llh = pd.DataFrame(np.zeros((A,6)), 
                   columns = ['Standard','Normal','AR(1)','Ext. AR(2)','Exog.','AR(1) Exog.'], 
                   index = colNames)

t_stat = pd.DataFrame(np.zeros((A,5)), 
                      columns = ['Normal','AR(1)','Ext. AR(2)','Exog.','AR(1) Exog.'], 
                      index = colNames)

p_val = pd.DataFrame(np.zeros((A,5)), 
                      columns = ['Normal','AR(1)','Ext. AR(2)','Exog.','AR(1) Exog.'], 
                      index = colNames)

parsN = pd.DataFrame(np.zeros((A,2)), 
                    columns = ['Mean','Volatility'], 
                    index = colNames)

parsO = pd.DataFrame(np.zeros((A,3)), 
                    columns = ['Mean','Volatility','AR(1)'], 
                    index = colNames)

parsT = pd.DataFrame(np.zeros((A,6)), 
                    columns = ['Mean','Volatility','AR(1)','AR(2)','Sq. AR(1)','Sq. AR(2)'], 
                    index = colNames)

parsX = pd.DataFrame(np.zeros((A,3)), 
                    columns = ['Mean','Volatility','Beta_X'], 
                    index = colNames)

parsARX = pd.DataFrame(np.zeros((A,4)), 
                    columns = ['Mean','Volatility','Beta_X','AR(1)'], 
                    index = colNames)

# Solver is sensitive to suggestions on these parameters
parNorm   = np.array([-0.04, 1.0])
parARone  = np.array([0.04, 1.0, 0.1])
parARtwoS = np.array([0.04, 1.0, 0.05, 0.04, 0.03, 0.02])
parX      = np.array([0.5, 1.0, 0.4])
parARX    = np.array([0.5, 1.0, 0.4, 0.5])

# Contain lists containing parameters and likelihood values, resp.

method = 'L-BFGS-B'
for i in range(A):
    # Standard computation
    llh.iloc[i,0]    = -modelStd(y.iloc[1:,i])
    # Normal test
    res = minimize(modelNorm, parNorm, args = y.iloc[1:,i], method = method)
    parsN.iloc[i,:2] = np.hstack(   ( res.x[0], np.exp(res.x[1]))  )
    llh.iloc[i,1]    = -res.fun
    t_stat.iloc[i,0] = testStat(llh.iloc[i,0], llh.iloc[i,1])
    p_val.iloc[i,0]  = 1 - stats.chi2.cdf(t_stat.iloc[i,0], 2)
    # AR(1) test
    res = minimize(modelARone, parARone, args = y.iloc[:,i], method = method)
    parsO.iloc[i,:]  = np.hstack(   ( res.x[0], np.exp(res.x[1]), res.x[2:] )   )
    llh.iloc[i,2]    = -res.fun
    t_stat.iloc[i,1] = testStat(llh.iloc[i,0], llh.iloc[i,2])
    p_val.iloc[i,1]  = 1 - stats.chi2.cdf(t_stat.iloc[i,1], 3)
    # AR(2) test with quadratic second lag
    res = minimize(modelARtwoS, parARtwoS, args = y.iloc[:,i], method = method)
    parsT.iloc[i,:]  = np.hstack(   ( res.x[0], np.exp(res.x[1]), res.x[2:] )   )
    llh.iloc[i,3]    = -res.fun
    t_stat.iloc[i,2] = testStat(llh.iloc[i,0], llh.iloc[i,3])
    p_val.iloc[i,2]  = 1 - stats.chi2.cdf(t_stat.iloc[i,2], 6)
    # Normal with exogenous regressor
    args = y.iloc[1:,i], div[:len(div)-1]
    res  = minimize(modelX, parX, args = args, method = method)
    parsX.iloc[i,:]  = np.hstack(   ( res.x[0], np.exp(res.x[1]), res.x[2:] )   )
    llh.iloc[i,4]    = -res.fun
    t_stat.iloc[i,3] = testStat(llh.iloc[i,0], llh.iloc[i,4])
    p_val.iloc[i,3]  = 1 - stats.chi2.cdf(t_stat.iloc[i,3], 3)
    # Normal with exogenous regressor and AR(1)
    args = y.iloc[:,i], div[:len(div)-1]
    res = minimize(modelARX, parARX, args = args, method = method)
    parsARX.iloc[i,:]  = np.hstack(   ( res.x[0], np.exp(res.x[1]), res.x[2:] )   )
    llh.iloc[i,5]    = -res.fun
    t_stat.iloc[i,4] = testStat(llh.iloc[i,0], llh.iloc[i,5])
    p_val.iloc[i,4]  = 1 - stats.chi2.cdf(t_stat.iloc[i,4], 4)



# parsN.round(4)
# parsO.round(4)
# parsT.round(4)
# parsX.round(4)
# parsARX.round(4)
llh[['Normal','AR(1)','Exog.','AR(1) Exog.']].round(2)
# t_stat.round(2)
# p_val.round(4)


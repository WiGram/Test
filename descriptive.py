"""
Date:    February 6th, 2019
Authors: Kristian Strand and William Gram
Subject: Describing Bloomberg time series

Description:
This script is strictly exploratory, considering
monthly Bloomberg data. Time series are illustrated
and the first two moments are estimated.
"""

import markowitzOpt as mpt
import numpy as np
import pandas as pd
import quandl
import scipy.optimize as opt
from scipy.optimize import minimize
from matplotlib import pyplot as plt
# import matplotlib.style as style
from numba import jit
from pandas_datareader import data as web
plt.rcParams.update(plt.rcParamsDefault)
plt.style.use('seaborn-paper')
np.set_printoptions(suppress = True)   # Disable scientific notation

# Read data into a Pandas data frame
bbData = pd.read_csv('/home/william/Dropbox/Thesis/mthReturns.csv', index_col=0,header=0)

# Set format of index to a date format
bbData.index = pd.to_datetime(bbData.index)

# Sort data with oldest data first
bbData = bbData.sort_index()

# Extract column names
colNames = list(bbData)

# Count amount of assets
assets = len(colNames)

# Define a vector d, to be used on the x-axis of plots
d = bbData.index

# Plot index price series
bbData.iloc[:,:len(colNames)].plot()
plt.show()

# Hard coded return and volatility column names
retList = ['HY_ret','IG_ret','CD_ret','R2_ret','R1_ret','SP_ret']

# Generate return time series for each index
for i in range(len(retList)):
    bbData[retList[i]] = bbData[colNames[i]].pct_change()

# Generate return correlation plots
import seaborn as sns
sns.pairplot(bbData.iloc[:,assets:2*assets])
plt.show()

# ============================================= #
# ===== Analysis of returns =================== #
# ============================================= #

# Applying log returns definition
monthlyRets = np.log(bbData.iloc[:,:assets]/bbData.iloc[:,:assets].shift(1))

# Histogram of mean returns
monthlyRets.hist(bins=100,figsize=(12,6))
plt.show()

# Time series plots of each return process
monthlyRets.plot(subplots = True, layout = (int(assets / 2), 2), figsize = (8,16))
plt.show()

# Moments and quartiles of return processes
monthlyRets.describe().transpose()

# ============================================= #
# ===== Analysis of volatility ================ #
# ============================================= #

# Var is squared return process, assuming true mean return of 0
monthlyVol = np.sqrt(monthlyRets ** 2)

# Time series plot of each squared return process
monthlyVol.plot(subplots = True, layout = (int(assets / 2), 2), figsize = (8,16))
plt.show()

# monthlyRets.cov() * 12 # Yearly covariance matrix
retCov = monthlyRets.cov()

# ============================================= #
# ===== Analysis of autocorrelation =========== #
# ============================================= #

def label(ax, string):
    ax.annotate(string, (1, 1), xytext=(-8, -8), ha='right', va='top',
                size=14, xycoords='axes fraction', textcoords='offset points')

fig, axes = plt.subplots(nrows=assets, figsize=(8, 12))
fig.tight_layout()

# Der antydes her en fejl. Dette ser ud til at være en falsk positiv - der er ingen fejl
for i in range(assets):
    pd.tools.plotting.autocorrelation_plot(monthlyRets.iloc[1:21,0], ax = axes[i])
    label(axes[i], colNames[i])
plt.show()

# ============================================= #
# ===== Analysis of optimal MPT portfolio ===== #
# ============================================= #

sims     = 50000
mptOutput = mpt.mptPortfolios(sims, monthlyRets, assets)
mpt.mptScatter(mptOutput['pfVol'], mptOutput['pfRet'],mptOutput['pfSR'],mptOutput['weights'],monthlyRets, n = 12)

"""
The end
"""
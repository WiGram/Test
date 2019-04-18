"""
This script will always contain hard-coded outputs from a
matlab script.

There is absolutely no intention of figuring out a way
for the two scripts to communicate.
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# ============================================= #
# ===== Two states ============================ #
# ============================================= #

idx = ['State 1', 'State 2']
states = len(idx)

labels = np.array([
    'High Yield',
    'Investment Grade',
    'Commodities',
    'Russell 2000',
    'Russell 1000'
])

llh = -4804.6401


"""
mu = np.array([
    [0.4688, -0.1432],
    [0.2543, -0.3492],
    [-0.0033, 0.1711],
    [0.5783, -0.2671],
    [0.7502, -0.1591]
])

"""
mu = np.array([
    [0.4688, 0.1432],
    [0.2543, 0.3492],
    [-0.0033, 0.1711],
    [0.5783, 0.2671],
    [0.7502, -0.1591]
])

cov = np.array([
    [
        [1.81257, 1.24255, 0.45237, 2.63926, 2.30530],
        [1.24255, 2.0454, -0.31163, 0.72401, 1.29577],
        [0.45237, -0.31163, 11.26467, 2.37891, 1.60384],
        [2.63926, 0.72401, 2.37891, 16.26595, 10.10013],
        [2.30530, 1.29577, 1.60384, 10.10013, 9.15257]
    ],
    [
        [13.69091, 2.76775, 4.41894, 18.21422, 12.76019],
        [2.76775, 3.33186, 1.78968, -0.21804, 0.63192],
        [4.41894, 1.78968, 30.69232, 6.10187, 3.72403],
        [18.21422, -0.21804, 6.10187, 71.31116, 47.10775],
        [12.76019, 0.63192, 3.72403, 47.10775, 40.73222]
    ]
])

probs = np.array([
    [0.94, 0.16],
    [0.06, 0.84]
])

# ============================================= #
# ===== Plotting ============================== #
# ============================================= #

sns.set_style('white')


def plot_moments(mu, cov, labels, idx, states):
    cov = [pd.DataFrame(
        cov[i],
        index=labels,
        columns=labels
    ) for i in range(states)]

    mask = np.ones_like(cov[0])
    mask[np.triu_indices_from(mask)] = False  # False error call

    for i in range(states):
        sns.heatmap(
            cov[i], annot=True, cmap='RdYlBu_r', mask=mask, linewidths=2
        )
        plt.title('Covariance matrix, starting in state {}'.format(i+1))
        plt.savefig(
            'C:/Users/willi/Dropbox/Thesis/Plots/'
            'cov{}_{}states.png'.format(i+1, states),
            bbox_inches='tight',
            pad_inches=0
        )
        plt.show()

    # ===== Mean returns ========================== #
    mus = pd.DataFrame(mu.T, index=idx, columns=labels)

    sns.heatmap(
        mus, annot=True, cmap='RdYlBu', linewidths=2
    )
    plt.title('Mean excess returns')
    plt.savefig(
        'C:/Users/willi/Dropbox/Thesis/Plots/mu_2states.png',
        bbox_inches='tight',
        pad_inches=0
    )
    plt.show()

    # ===== SR ==================================== #
    SR = pd.DataFrame(
        [mu[:, i].T/np.sqrt(np.diag(cov[i])) for i in range(states)],
        index=idx,
        columns=labels
    )

    sns.heatmap(
        SR, annot=True, cmap='RdYlBu', linewidths=2
    )
    plt.title('Sharpe Ratios')
    plt.savefig(
        'C:/Users/willi/Dropbox/Thesis/Plots/SR_{}states.png'.format(states),
        bbox_inches='tight',
        pad_inches=0
    )
    plt.show()

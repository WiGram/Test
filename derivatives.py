import numpy as np

def firstMu(pS, returns, mu, vol):
    return pS * (returns - mu) / vol ** 2

def firstVol(pS, returns, mu, vol):
    return -0.5 * pS * (1 / vol ** 2 - (returns - mu) ** 2 / vol ** 4)

def firstPj(pST, returns, pj, pN):
    return pST * (1 / pj - 1 / pN)

def secondMuMu(pS, returns, mu, vol):
    return - sum(pS / vol ** 4)

def secondVolVol(pS, returns, mu, vol):
    return - sum( pS * ((returns - mu) ** 2 / vol ** 6 - 0.5 * 1 / vol ** 4))

def secondPjPj(pST, returns, pj, pN):
    return -sum(pST * (1 / pj ** 2 - 1 / pN ** 2))

def secondPNPN(pST, returns, pj, pN):
    return -secondPjPj(pST, returns, pj, pN)

def secondMuVol(pS, returns, mu, vol):
    return - sum(pS * (returns - mu) / vol ** 4)

def score(pS, pST, rets, mu, vol, p):
    S = len(mu)
    T = len(rets)
    pST = pST.reshape(S,S,T)
    m = np.array([firstMu(pS[s,:], rets, mu[s], vol[s]) for s in range(S)])
    v = np.array([firstVol(pS[s,:], rets, mu[s], vol[s]) for s in range(S)])

    pj = np.zeros((S,S,T))
    pj[:S-1,:S,:T] = np.array([[firstPj(pST[i,j,:], rets[:], p[i,j], p[i,S-1]) for i in range(S)] for j in range(S-1)])
    pj[S-1,:S,:T]  = np.array([firstPj(pST[i,S-1,:], rets[:], p[i,S-1], p[i,0]) for i in range(S)])

    score = np.concatenate((m, v, pj.reshape(9,T)))

    product = np.array([np.outer(score[:,t], score[:,t]) for t in range(T)])

    return np.diag(np.sum(product, axis = 0) / T)


"""
test4 = score(pS, pST, rets, ms[ms.shape[0]-1, 0, :], vs[vs.shape[0]-1, :, 0, 0], ps[ps.shape[0]-1, :, :])
"""
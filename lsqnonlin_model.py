import numpy as np
import pandas as pd


class CalcBoldTI:
    def __init__(self, x=None, data=None, TIlist=None, BOLD=None, T1vec=None):
        self.data = data
        self.TIlist = TIlist
        self.BOLD = BOLD
        self.T1vec = T1vec
        self.A = x[0:-2]
        self.nlayers = len(self.A)
        self.nTI = len(self.TIlist)
        self.S0 = x[-1]

    def generate_newdata(self, nTI, nlayers, S0, TIlist, T1vec, A, BOLD):
        """

        :param nTI:
        :param nlayers:
        :param S0:
        :param TIlist:
        :param T1vec:
        :param A:
        :param BOLD:
        :return:
        """
        newdata = np.zeros((10, nTI, nlayers))
        for j in range(nTI):
            for i in range(nlayers):
                newdata[:, j, i] = (
                    S0 * (1 - 2 * np.exp(-TIlist[j] / T1vec[i])) * A[i] * BOLD.values
                )
        newdata = np.sum(newdata, axis=2)
        newdata = np.abs(newdata)
        newdata = np.transpose(newdata)
        return newdata

    def normalize_newdata(self, newdata):
        for i in range(np.size(newdata, 0)):
            newdata[i, :] = newdata[i, :] / np.sum(newdata[i, :])
        return newdata

    def calc_err(self, data, newdata):
        err = newdata - data
        err = err.values.flatten()
        return err

    def run(self):
        newdata = self.generate_newdata(
            nTI=self.nTI,
            nlayers=self.nlayers,
            S0=self.S0,
            TIlist=self.TIlist,
            T1vec=self.T1vec,
            A=self.A,
            BOLD=self.BOLD,
        )
        newdata = self.normalize_newdata(newdata=newdata)
        err = self.calc_err(data=self.data, newdata=newdata)
        return err

#%%
import numpy as np
import numpy.matlib as mat
import pandas as pd
import os
import glob
import seaborn as sns
import matplotlib.pyplot as plt

#%%
PATH = os.path.abspath("C:/Users/Owner/Desktop/Cortical_layers_fMRI")
path = r"{0}/derivatives/tsplots/mean_ts".format(PATH)
ACTIONS = ["Motor", "Sensory"]
#%%
class ModelResults:
    def __init__(self, subj, path: str = PATH):
        """
        :param subj: Integer or string - number of subject or 'Mean'
        :param path: Mother directory of analysis
        """
        self.path = r"{0}/derivatives/tsplots/mean_ts".format(path)
        self.subj = subj

    #%%
    def get_mean_data(self, action: str, path: str):
        FieldNames = [
            "SE-EPI",
            "IREPITI630",
            "IREPITI650",
            "IREPITI670",
            "IREPITI690",
            "IREPITI710",
            "IREPITI730",
            "IREPITI750",
        ]
        all_data = pd.DataFrame()
        for field in FieldNames:
            file_name = r"task-{0}_acq-{1}_bold".format(action, field)
            prot_file = pd.read_csv(
                r"{0}/{1}/{1}_subjects_norm_BOLD_response.txt".format(path, file_name)
            )
            if "IR" in field:
                mean_prot = prot_file.mean(axis=1).rename(int(field[-3:]))
            else:
                mean_prot = prot_file.mean(axis=1).rename(field[-3:])
            all_data = all_data.append(mean_prot)
        BOLD = all_data.iloc[0:1, :].mean()
        data = all_data.iloc[1:]
        TIlist = []
        for TI in data.index:
            TIlist.append(TI)
        return BOLD, data, TIlist

    def get_subject_data(self, subj, action):
        """
        Extrcting subject's mean normalized time course
        :param subj: Subject`s number : int
        :param action: {"Motor" or "Sensory"} :return: BOLD: SE or GE time course,
        data: nx10 array, where n is the number of IR-SE protocols the subject went through
        """
        FieldNames = [
            "SE-EPI",
            "IREPITI630",
            "IREPITI650",
            "IREPITI670",
            "IREPITI690",
            "IREPITI710",
            "IREPITI730",
            "IREPITI750",
            "IREPITI930",
        ]
        all_data = pd.DataFrame()
        if type(subj) == int:
            if subj >= 10:
                subj = str(subj)
            else:
                subj = "0" + str(subj)
        for field in FieldNames:
            file_name = r"task-{0}_acq-{1}_bold".format(action, field)
            this_prot = glob.glob(
                r"{0}/{1}/{2}".format(
                    os.path.dirname(self.path), "sub-" + subj, file_name
                )
            )
            if this_prot.__len__() != 0:
                subj_prot = pd.read_csv(
                    r"{0}/{1}/{1}_subjects_norm_BOLD_response.txt".format(
                        self.path, file_name
                    )
                ).get("sub-" + subj)
                subj_prot.name = field
                if "Gre" in field:
                    fixed_subj_prot = np.zeros(int(len(subj_prot) / 2))
                    j = 0
                    for i in range(len(fixed_subj_prot)):
                        fixed_subj_prot[i] = np.mean([subj_prot[j], subj_prot[j + 1]])
                        j += 2
                all_data = all_data.append(subj_prot, verify_integrity=True)
        BOLD = all_data.iloc[0, :]
        data = all_data.iloc[1:, :].dropna(axis=1)
        TIlist = []
        for TI in data.index:
            TIlist.append(int(TI[-3:]))
        return BOLD, data, TIlist

    #%%
    def normalize_data(self, data):
        norm_data = (
            np.array([data - data.min()]) / np.array([data.max() - data.min()])[0]
        )
        return norm_data

    def gen_BOLD_mat(self, BOLD):
        BOLD = mat.repmat(BOLD, 7, 1)
        BOLD = BOLD.transpose()
        return BOLD

    def gen_initial_params(self):
        s0 = 5000
        T1 = np.array(
            [890, 1000, 1100, 1300, 1400, 1600]
        )  # TO BE REPLACED WITH ACTUAL T1 VALUES
        TR = 3000
        return s0, T1, TR

    def gen_inital_cont_guess(self, TIlist, T1, TR):
        A = np.zeros([len(T1), len(TIlist)])
        for i in range(len(TIlist)):
            fix = 1 - np.exp(-(TR - TIlist[i]) / T1)
            A[:, i] = 1 - (1 + (fix)) * np.exp(-TIlist[i] / T1)
            A = abs(A)
        return A

    def calc_correlation(self, A, BOLD, norm_mean_data):
        st1 = np.zeros([10, 7, 6])
        mst1 = np.zeros([7, 6])
        cor = np.zeros([A.shape[0], 1])
        pval = np.zeros([A.shape[0], 1])
        for i in range(A.shape[0]):
            st1[:, :, i] = abs(mat.repmat(A[i, :], 10, 1)) * BOLD
            mst1[:, i] = np.mean(st1[4:8, :, i], axis=0)
            [res1, res2] = np.corrcoef(mst1[:, i], norm_mean_data)
            cor[i] = res1[1]
            pval[i] = res1[0]
        return cor, pval

    def run_model(self):
        if type(self.subj) == str:
            res = pd.DataFrame(columns=ACTIONS)
            for action in ACTIONS:
                BOLD, data, TIlist = self.get_mean_data(path=self.path, action=action)
                mean_data = data.iloc[:, 3:7].mean(axis=1)
                norm_mean_data = self.normalize_data(data=mean_data)
                BOLD = self.gen_BOLD_mat(BOLD=BOLD)
                s0, T1, TR = self.gen_initial_params()
                A = self.gen_inital_cont_guess(TIlist=TIlist, T1=T1, TR=TR)
                cor, pval = self.calc_correlation(
                    A=A, BOLD=BOLD, norm_mean_data=norm_mean_data
                )
                res[action] = cor[:, 0]
                # res[action] = self.normalize_data(data=cor)[0][:, 0]
                res = res.set_index(T1)
            return res
        else:
            res = pd.DataFrame(columns=ACTIONS)
            for action in ACTIONS:
                BOLD, data, TIlist = self.get_subject_data(
                    subj=self.subj, action=action
                )
                mean_data = data.iloc[:, 3:7].mean(axis=1)
                norm_mean_data = self.normalize_data(data=mean_data)
                BOLD = self.gen_BOLD_mat(BOLD=BOLD)
                s0, T1, TR = self.gen_initial_params()
                A = self.gen_inital_cont_guess(TIlist=TIlist, T1=T1, TR=TR)
                cor, pval = self.calc_correlation(
                    A=A, BOLD=BOLD, norm_mean_data=norm_mean_data
                )
                # res[action] = cor[:, 0]
                res[action] = self.normalize_data(data=cor)[0][:, 0]
                res = res.set_index(T1)
            return res

    def plot_results(self):
        """
        Plotting the results calculated by the fMRI of cortical layers model
        :return: Motor and Sensory parameters as extracted from the model, and the T1 values calculated
        """
        res = self.run_model()
        barM = res["Motor"].values
        barS = res["Sensory"].values
        ind = res.index
        T1vec = np.zeros(len(ind))
        for i in range(len(T1vec)):
            T1vec[i] = int(ind[i])
        barWidth = 25
        r2 = [x + barWidth for x in T1vec]
        plt.grid(b=True, linewidth=0.2)
        plt.bar(
            T1vec, barM, color="b", width=barWidth, edgecolor="white", label="Motor"
        )
        plt.bar(r2, barS, color="r", width=barWidth, edgecolor="white", label="Sensory")
        plt.plot(T1vec, barM)
        plt.plot(T1vec, barS)
        plt.xlabel("T1", fontweight="bold")
        plt.ylabel("Partial contribution", fontweight="bold")
        plt.legend()
        plt.title(
            "Partial contribution of cortical layers to motor and sensory operations"
        )
        plt.show()
        return barM, barS, T1vec


#%%

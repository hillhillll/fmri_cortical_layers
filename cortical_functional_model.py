import scipy.io
import scipy.optimize
import os
import numpy as np
import pandas as pd
import glob
import lsqnonlin_model
import matplotlib.pyplot as plt
import seaborn as sns

PATH = os.path.abspath("C:/Users/Owner/Desktop/fsl_pipeline_trial")
PREV_DATA = scipy.io.loadmat(
    file_name=r"C:\Users\Owner\Desktop\cortical_layer_results\anatomical_layers.mat",
    variable_names=["GMs_prop", "T1Histograms"],
)
GMs = PREV_DATA["GMs_prop"]
T1Histograms = PREV_DATA["T1Histograms"]


class ModelResults:
    def __init__(self, subj, path: str = PATH):
        """
        :param subj: Integer or string - number of subject or 'Mean'
        :param path: Mother directory of analysis
        """
        self.path = r"{0}/derivatives/tsplots/mean_ts".format(path)
        if subj == 0:
            raise Exception(
                "Subject 1 never went through anatomical cortical layer classification!"
            )
        self.subj = subj

    def calc_mean_vals(self):
        T1vec = GMs.mean(0)
        return T1vec

    def T1_extraction(self, subj):
        if subj != "Mean":
            T1vec = GMs[subj]
            print("T1 values extracted for subject {0} are: {1}".format(subj, T1vec))
        else:
            T1vec = self.calc_mean_vals()
            print("Mean T1 values extracted are: {0}".format(T1vec))
        return T1vec

    def extract_initial_params(self, T1vec: np.ndarray):
        """
        Creates an initial guess vector for the MLS function
        :param T1vec: T1 values as extracted from the GM model
        :return: x0 (initial guesses), min_val and max_val (low and high boundaries for the MLS, accordingly)
        """
        compN = len(T1vec)
        layer_guess = np.random.random(compN)
        layer_guess = layer_guess / layer_guess.sum()
        layer_guess = layer_guess.tolist()
        s0 = 5000 * np.random.rand() + 5000
        x0 = [layer_guess, s0]
        min_val = [np.zeros(compN).tolist(), 5000]
        max_val = [np.ones(compN).tolist(), 10000]
        x0 = np.asarray(x0[0])
        return x0, min_val, max_val

    def define_optimset(self):
        """
        Define parameters for optimization
        :return: max_nfev : Maximum number of function evaluations before the termination.
        ftol : Tolerance for termination by the change of the cost function.
        xtol : Tolerance for termination by the change of the independent variables.
        method : Algorithm to perform minimization. (‘lm’ : Levenberg-Marquardt algorithm.)
        """
        max_nfev = 2000
        ftol = 1e-6
        xtol = 1e-6
        method = "lm"
        return max_nfev, ftol, xtol, method

    def get_subject_data(self, subj, action):
        """
        Extrcting subject's mean normalized time course
        :param subj: Subject`s number : int
        :param action: {"Motor" or "Sensory"} :return: BOLD: SE or GE time course,
        data: nx10 array, where n is the number of IR-SE protocols the subject went through
        """
        FieldNames = [
            "SE-EPI",
            "Gre",
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

    def get_mean_data(self, action: str):
        FieldNames = [
            "SE-EPI",
            "Gre",
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
        for field in FieldNames:
            file_name = r"task-{0}_acq-{1}_bold".format(action, field)
            prot_file = pd.read_csv(
                r"{0}/{1}/{1}_subjects_norm_BOLD_response.txt".format(
                    self.path, file_name
                )
            )
            if "IR" in field:
                mean_prot = prot_file.mean(axis=1).rename(int(field[-3:]))
            else:
                mean_prot = prot_file.mean(axis=1).rename(field[-3:])
            if "Gre" in field:
                fixed_subj_prot = np.zeros(int(len(mean_prot) / 2))
                j = 0
                for i in range(len(fixed_subj_prot)):
                    fixed_subj_prot[i] = np.mean([mean_prot[j], mean_prot[j + 1]])
                    j += 2
                mean_prot = pd.Series(fixed_subj_prot)
                mean_prot.name = "BOLD"
            all_data = all_data.append(mean_prot)
        BOLD = all_data.iloc[0:1, :].mean()
        data = all_data.iloc[2:]
        TIlist = []
        for TI in data.index:
            TIlist.append(TI)
        return BOLD, data, TIlist

    def run_calcbolddti(self, x=None, data=None, TIlist=None, BOLD=None, T1vec=None):
        if x is None or data is None or TIlist is None or BOLD is None or T1vec is None:
            T1vec = self.T1_extraction(subj=self.subj)
            x, min_val, max_val = self.extract_initial_params(T1vec=T1vec)
            BOLD, data, TIlist = self.get_subject_data(
                subj=self.subj, action="Motor"
            )  ### Fix action
        err_calc = lsqnonlin_model.CalcBoldTI(x, data, TIlist, BOLD, T1vec)
        err = err_calc.run()
        return err

    def run_model(self):
        actions = ["Motor", "Sensory"]
        LayerParams = []
        for cur_act in actions:
            if type(self.subj) == int:
                BOLD, data, TIlist = self.get_subject_data(
                    subj=self.subj, action=cur_act
                )
            else:
                BOLD, data, TIlist = self.get_mean_data(action=cur_act)
            T1vec = self.T1_extraction(self.subj)
            x0, min_val, max_val = self.extract_initial_params(T1vec=T1vec)
            max_nfev, ftol, xtol, method = self.define_optimset()
            LayerParams.append(
                scipy.optimize.least_squares(
                    fun=self.run_calcbolddti,
                    x0=x0,
                    max_nfev=max_nfev,
                    ftol=ftol,
                    xtol=xtol,
                    method=method,
                    kwargs={
                        "data": data,
                        "TIlist": TIlist,
                        "BOLD": BOLD,
                        "T1vec": T1vec,
                    },
                )
            )
        return LayerParams

    def plot_results(self):
        """
        Plotting the results calculated by the fMRI of cortical layers model
        :return: Motor and Sensory parameters as extracted from the model, and the T1 values calculated
        """
        [m, s] = self.run_model()
        barM = m.x[2:8]
        barS = s.x[2:8]
        T1vec = self.T1_extraction(self.subj)
        for i in T1vec:
            T1vec[T1vec == i] = int(i)
        T1vec = T1vec[2:8]
        barWidth = 25
        r2 = [x + barWidth for x in T1vec]
        plt.grid(b=True, linewidth=0.2)
        plt.bar(
            T1vec, barM, color="b", width=barWidth, edgecolor="white", label="Motor"
        )
        plt.bar(r2, barS, color="r", width=barWidth, edgecolor="white", label="Sensory")
        plt.xlabel("T1", fontweight="bold")
        plt.ylabel("Partial contribution", fontweight="bold")
        plt.legend()
        plt.title(
            "Partial contribution of cortical layers to motor and sensory operations"
        )
        plt.show()
        return barM, barS, T1vec

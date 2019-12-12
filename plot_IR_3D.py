import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os
import export_excels
from plot_nullify import PlotTIs
from scipy.signal import savgol_filter

PATH = os.path.abspath(r"C:/Users/Owner/Desktop/Cortical_layers_fMRI")
TIS = np.arange(630, 761, 10)


class PlotIR:
    def __init__(self, path=PATH):
        self.path = path
        self.actions = ["Motor", "Sensory"]

    def generate_excels(self, path=""):
        if not path:
            path = self.path
        gen_exc = export_excels.CreateExcels(path=path)
        gen_exc.export_info()

    def create_df(self, path="", action=""):
        if not path:
            path = self.path
        path = r"{0}/derivatives/tsplots/mean_ts".format(path)
        df = pd.read_excel(
            r"{0}/task-{1}_acq-IREPITI_summary.xlsx".format(path, action)
        ).iloc[:, 1:]
        return df

    def plot_IRSE(self, action, df, path=""):
        if not path:
            path = self.path
        path = r"{0}/derivatives/tsplots/mean_ts".format(path)
        fig, ax = plt.subplots(figsize=[10, 5])
        ax = fig.add_subplot(111, projection="3d")
        ax.set_title(
            "{0} normalized mean BOLD response in relevance to TI".format(action)
        )
        ax.set_ylabel("TI (ms)")
        ax.set_xlabel("Time point")
        ax.set_zlabel("Normalized BOLD")
        for i in range(df.columns.size):
            Z = df.iloc[:, i]
            Y = np.repeat(int(df.columns[i][-3:]), len(df))
            X = np.array(range(1, len(df) + 1))
            ax.plot3D(X, Y, Z, color="blue")
            ax.view_init(elev=30.0, azim=-15)
            # %%
        get_data = PlotTIs(path=self.path)
        data_df, std_df = get_data.gather_data(
            path=get_data.path, action=action, filetype=get_data.filetype
        )
        err = std_df.values[0]
        mean_peak = data_df.values[0]
        z = poly_smooth(mean_peak=mean_peak)
        z = savgol_filter(z, len(z) - 1, 7)
        X = np.repeat(X.mean(), len(z))
        print(len(X), len(TIS), len(z))
        if "Motor" in action:
            color = "red"
        else:
            color = "green"
        ax.plot3D(X, TIS, z.flatten(), color=color)
        # for i in range(len(err)):
        #     ax.plot([X[i], X[i]], [Y[i], Y[i]], [mean_peak[i] + err[i], mean_peak[i] - err[i]], marker="_")
        plt.savefig(r"{0}/task-{1}_acq-IREPITI_summary.png".format(path, action))
        return ax, data_df, std_df

    def run(self):
        self.generate_excels(self.path)
        for action in self.actions:
            df = self.create_df(path=self.path, action=action)
            ax = self.plot_IRSE(action=action, df=df)
        return ax


def poly_smooth(mean_peak):
    z = np.zeros((1, len(mean_peak) * 2), dtype=float)[0]
    j = 0
    for i in range(0, z.size, 2):
        z[i] = mean_peak[j]
        z[i + 1] = np.mean([z[i], mean_peak[j]])
        j += 1
    return z

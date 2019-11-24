import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os
import export_excels

PATH = os.path.abspath(r"C:/Users/Owner/Desktop/fsl_pipeline_trial")


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
        ).iloc[:, 1:-2]
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
            ax.plot3D(X, Y, Z)
            ax.view_init(elev=32.0, azim=-18)
            # %%
        plt.show()
        plt.savefig(r"{0}/task-{1}_acq-IREPITI_summary.png".format(path, action))

    def run(self):
        self.generate_excels(self.path)
        for action in self.actions:
            df = self.create_df(path=self.path, action=action)
            self.plot_IRSE(action=action, df=df)

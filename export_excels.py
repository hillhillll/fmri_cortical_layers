import pandas as pd
import glob
import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d import Axes3D

ACTIONS = ["Motor", "Sensory"]
ACQS = ["SE", "IREPITI"]


class CreateExcels:
    def __init__(self, path: str = r"C:/Users/Owner/Desktop/fsl_pipeline_trial"):
        self.path = "{0}/derivatives/tsplots/mean_ts".format(path)

    def gather_txt_files(self, action: str, acq: str):
        files = glob.glob(
            r"{0}/task-{1}_acq-{2}*/*mean_norm_bold_response.txt".format(
                self.path, action, acq
            )
        )
        return files

    def gather_excels(self, action: str, acq: str):
        file = glob.glob(
            r"{0}/task-{1}_acq-{2}_summary.xlsx".format(self.path, action, acq)
        )
        return file

    def export_info(self):
        for action in ACTIONS:
            for acq in ACQS:
                files = self.gather_txt_files(action=action, acq=acq)
                df = pd.read_csv(files[0])
                for f in files[1:]:
                    df_new = pd.read_csv(f)
                    df = pd.concat([df, df_new], axis=1)
                df.to_excel(
                    r"{0}/task-{1}_acq-{2}_summary.xlsx".format(self.path, action, acq)
                )

    def export_pngs(self):
        for action in ACTIONS:
            for acq in ACQS:
                file = self.gather_excels(action=action, acq=acq)
                df = pd.read_excel(file[0], index_col=0)
                if "IREPITI" not in acq:
                    ax = df.plot(kind="line", figsize=(10, 5))
                    ax.set_xlabel("Time point")
                    ax.set_ylabel("Normalized signal")
                else:
                    fig, ax = plt.subplots(figsize=[10, 5])
                    ax = fig.add_subplot(111, projection="3d", azim=-15)
                    ax.set_ylabel("TI (ms)")
                    ax.set_xlabel("Time point")
                    ax.set_zlabel("Normalized signal")
                    for i in range(df.columns.size):
                        Z = df.iloc[:, i]
                        Y = np.repeat(int(df.columns[i][-3:]), len(df))
                        X = np.array(range(1, len(df) + 1))
                        ax.plot3D(X, Y, Z)
                ax.set_title(
                    "Mean BOLD response for {0} {1} protocols".format(action, acq)
                )

                ax.grid(color="grey", linestyle="-", linewidth=0.25, alpha=0.5)
                fig = ax.get_figure()
                fig.savefig(
                    r"{0}/task-{1}_acq-{2}_summary.png".format(self.path, action, acq)
                )

    def plot_irepiti(self):
        fig, ax = plt.subplots(figsize=[10, 5])
        ax = fig.add_subplot(111, projection="3d")
        ax.set_ylabel("TI (ms)")
        ax.set_xlabel("Time (ms)")
        ax.set_zlabel("Normalized BOLD")
        for i in range(df.columns.size):
            Z = df.iloc[:, i]
            Y = np.repeat(int(df.columns[i][-3:]), len(df))
            X = np.array(range(1, len(df) + 1))
            ax.plot3D(X, Y, Z)

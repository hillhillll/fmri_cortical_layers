import glob
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.signal import savgol_filter

ACTIONS = ["Motor", "Sensory"]
FILETYPE = "subjects_norm_BOLD_response"


class PlotTIs:
    def __init__(
        self,
        path: str = r"C:/Users/Owner/Desktop/Cortical_layers_fMRI",
        filetype: str = FILETYPE,
        sig_change=True,
        ax=None,
        normalize: bool = True,
    ):
        self.path = "{0}/derivatives/tsplots/mean_ts".format(path)
        self.filetype = filetype
        self.sig_change = sig_change
        self.ax = ax
        self.normalize = normalize

    def gather_data(self, path: str, action: str, filetype: str):
        rel_files = glob.glob("{0}/*{1}*/*{2}.txt".format(path, action, filetype))
        data_df = pd.DataFrame()
        std_df = pd.DataFrame()
        for f in rel_files:
            header = f.split("_")[-6]
            df = pd.read_csv(f).iloc[3:7]
            data = pd.DataFrame(df.mean(axis=1)).mean()
            std = pd.DataFrame(df.sem(axis=1)).mean()
            data_df[header] = data.values
            std_df[header] = std.values
        data_df = data_df.drop("acq-SE-EPI", axis=1)
        std_df = std_df.drop("acq-SE-EPI", axis=1)
        return data_df, std_df

    def plot_data(
        self,
        data_df: pd.DataFrame,
        std_df: pd.DataFrame,
        action: str,
        ax=None,
        both: bool = False,
    ):
        X = np.arange(
            int(data_df.columns[0][-3:]), int(data_df.columns[-1][-3:]) + 11, 10
        )
        # for i in data_df.columns:
        #     X.append(int(i[-3:]))
        data = data_df.values[0]
        true_err = std_df.values[0]
        if not ax:
            fig, ax = plt.subplots(figsize=[10, 5])
        if both:
            ax.set_title("Normalized mean peak BOLD response in relevance to TI")
            ax.set_xlabel("TI (ms)")
            ax.set_ylabel("Normalized mean peak BOLD response")
        else:
            ax.set_title(
                "{0} mean peak BOLD response in relevance to TI".format(action)
            )
            ax.set_xlabel("TI (ms)")
            ax.set_ylabel("Mean peak BOLD response".format(action))
        smoothed_data = poly_smooth(mean_peak=data)
        smoothed_data = savgol_filter(smoothed_data, len(smoothed_data) - 1, 7)
        if both:
            smoothed_data = (smoothed_data - smoothed_data.min()) / (
                smoothed_data.max() - smoothed_data.min()
            )
        if "Motor" in action:
            color = "red"
        else:
            color = "green"
        ax.plot(X, smoothed_data, label=action, color=color)
        err = np.zeros(len(smoothed_data))
        j = 0
        for i in range(0, len(err), 2):
            err[i] = true_err[j]
            j += 1
        ax.errorbar(
            X,
            smoothed_data,
            yerr=err,
            fmt="o",
            ecolor="orange",
            linewidth=1.5,
            capsize=1,
        )

        ax.grid(color="grey", linestyle="-", linewidth=0.25, alpha=0.5)
        ax.legend()
        return ax

    def run(self):
        for action in ACTIONS:
            ax = None
            data_df, std_df = self.gather_data(
                path=self.path, action=action, filetype=self.filetype
            )
            ax = self.plot_data(data_df=data_df, std_df=std_df, action=action, ax=ax)
            plt.savefig(
                r"{0}/{1} signal change in relevance to TI.png".format(
                    self.path, action
                )
            )
        ax = None
        for action in ACTIONS:
            data_df, std_df = self.gather_data(
                path=self.path, action=action, filetype=self.filetype
            )
            ax = self.plot_data(
                data_df=data_df, std_df=std_df, action=action, ax=ax, both=True
            )
        plt.savefig(
            r"{0}/Normalized signal change in relevance to TI.png".format(self.path)
        )


def poly_smooth(mean_peak):
    z = np.zeros((1, len(mean_peak) * 2), dtype=float)[0]
    j = 0
    for i in range(0, z.size, 2):
        z[i] = mean_peak[j]
        z[i + 1] = np.mean([z[i], mean_peak[j]])
        j += 1
    return z

#%%
import glob
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from mpl_toolkits import mplot3d
from scipy.ndimage.filters import gaussian_filter1d


class PlotTIs:
    def __init__(
        self,
        action: str = "Motor",
        path: str = r"C:/Users/Owner/Desktop/Cortical_Layers_fMRI",
        filetype: str = "subjects_norm_BOLD_response",
        sig_change=True,
        ax=None,
        normalize: bool = True,
    ):
        self.action = action
        self.path = "{0}/derivatives/tsplots/mean_ts".format(path)
        self.filetype = filetype
        self.sig_change = sig_change
        self.ax = ax
        self.normalize = normalize

    def plot(
        self, action="", path="", filetype="", sig_change=True, ax="", normalize=""
    ):
        if not action:
            action = self.action

        if not path:
            path = self.path

        if not filetype:
            filetype = self.filetype
        if not sig_change:
            sig_change = self.sig_change
        if not ax:
            ax = self.ax
        if not normalize:
            normalize = self.normalize

        all_files = glob.glob(
            "{0}/*/*{1}*IREPITI*{2}.txt".format(path, action, filetype)
        )
        df = pd.read_csv(all_files[0], header=0)  # initiate df
        header = all_files[0].split("_")[-6]  # acq name
        mean_df = df.mean(axis=1)  # initiate mean
        std_df = df.max() - df.min()  # initiate std
        mean_df = mean_df.to_frame()
        std_df = std_df.to_frame()
        mean_df.columns = pd.MultiIndex.from_product([[header]])
        std_df.columns = pd.MultiIndex.from_product([[header]])
        for f in all_files[1:]:  # concatenate next dfs
            if '930' not in f:
                df = pd.read_csv(f, header=0)
                header = f.split("_")[-6]
                this_mean = df.mean(axis=1)
                this_std = df.max() - df.min()
                this_mean = this_mean.to_frame()
                this_std = this_std.to_frame()
                this_mean.columns = pd.MultiIndex.from_product([[header]])
                this_std.columns = pd.MultiIndex.from_product([[header]])
                mean_df = mean_df.join(this_mean)
                std_df = std_df.join(this_std)
        #%%
        # Plot 2D or 3D
        if not ax:
            fig, ax = plt.subplots(figsize=[10, 5])
            # legs = [Action]

        if sig_change:
            signal_change = mean_df.max() - mean_df.min()
            if normalize:
                signal_change = (signal_change - signal_change.min()) / (
                    signal_change.max() - signal_change.min()
                )
            std_df = np.sqrt((std_df - signal_change) ** 2) / np.sqrt(
                len(std_df.keys())
            )
            std_df = pd.DataFrame(
                data=[std_df.max().values, std_df.min().values],
                index=["max", "min"],
                columns=std_df.columns,
            )
            error = [std_df.max().values, std_df.min().values]
            signal_change = gaussian_filter1d(signal_change, sigma=0.5)
            X = []
            for i in mean_df.columns:
                i = i[0]
                X.append(int(i[-3:]))
            ax.plot(X, signal_change, label=action)
            ax.errorbar(X, signal_change, yerr=error, fmt="o", linewidth=1.5, capsize=1)
            ax.set_title("Normalized signal change in relevance to TI")
            ax.set_xlabel("TI (ms)")
            ax.set_ylabel("Normalized percent signal change")
            ax.grid(color="grey", linestyle="-", linewidth=0.25, alpha=0.5)
            leg = ax.legend()
            plt.show()

            return mean_df, signal_change, ax

    def run(self):
        df, signal_change, ax = self.plot(
            action=self.action,
            path=self.path,
            filetype=self.filetype,
            sig_change=self.sig_change,
            ax=self.ax,
        )
        return df, signal_change, ax

    def run_and_save(self):
        df_sensory, signal_change_sensory, ax_sensory = self.plot(
            action="Sensory",
            path=self.path,
            filetype=self.filetype,
            sig_change=self.sig_change,
        )
        plt.savefig(
            r"{0}/Sensory signal change in relevance to TI.png".format(self.path)
        )

        df_motor, signal_change_motor, ax_motor = self.plot(
            action="Motor",
            path=self.path,
            filetype=self.filetype,
            sig_change=self.sig_change,
        )
        plt.savefig(r"{0}/Motor signal change in relevance to TI.png".format(self.path))

        df_both, signal_change_both, ax_both = self.plot(
            action="Sensory",
            path=self.path,
            filetype=self.filetype,
            sig_change=self.sig_change,
            ax=ax_motor,
        )
        plt.savefig(
            r"{0}/Normalized signal change in relevance to TI.png".format(self.path)
        )
        return df_both, signal_change_both, ax_both


#%%

import numpy as np
import pandas as pd
import glob
import os


## s = fixed ts
## x = normalized ts
TIS = ['630','650','670','690','710','730','750']

class CalcMeanTS:
    def __init__(self, path: str = r"C:/Users/Owner/Desktop/trial_2"):
        self.path = "{0}/derivatives/tsplots/mean_ts".format(path)

    def get_ts_file(self, path: str):
        ts_files = glob.glob("{0}/*/*all_ts.txt".format(path))
        return ts_files

    def calc_ts_properties(self, ts_files: list):
        for f in ts_files:
            ts = pd.read_csv(f, header=0, sep=",")
            # new_f = f.replace("all_ts", "fixed_ts")
            scaled_file = f.replace("all_ts", "normalized_ts")
            mean_scaled_file = f.replace("all_ts", "mean_normalized_ts")
            mean_b_f = f.replace("all_ts", "mean_norm_bold_response")
            # mean_real_b = f.replace("all_ts", "mean_bold_response")
            if "SE" in f and ["Sensory" or "Motor" in f][0]:
                s = ts[3:44].reset_index(drop=True)
            else:
                s = ts[2:43].reset_index(drop=True)
            subjects = list(s.columns.values)
            header = f.split("_")[-4]
            scaled = (s - s.min()) / (s.max() - s.min())
            scaled_mean = scaled.mean(axis=1)
            scaled_mean.to_csv(
                mean_scaled_file,
                header=[header],
                mode="w",
                index=False,
                line_terminator=os.linesep,
            )
            scaled.to_csv(
                scaled_file,
                header=subjects,
                mode="w",
                index=False,
                line_terminator=os.linesep,
            )

    def calculate_subjects_mean_bold(self, path: str):
        ts_files = glob.glob("{0}/*/*bold_normalized_ts.txt".format(path))
        for f in ts_files:
            df = pd.read_csv(f)
            if "Gre" in f:
                relevant = df[1:81]
                BOLD_duration = 20
            else:
                relevant = df[1:41]
                BOLD_duration = 10
            iterables = [
                ["First", "Second", "Third", "Fourth"],
                np.arange(BOLD_duration).tolist(),
            ]
            index = pd.MultiIndex.from_product(iterables, names=["Action", "Time"])
            mean_bold_df = pd.DataFrame(
                relevant.values, index=index, columns=relevant.columns
            )
            mean_bold_df = mean_bold_df.mean(level="Time")
            mean_bold_df.to_csv(
                f.replace("normalized_ts", "subjects_norm_BOLD_response"),
                mode="w",
                index=False,
                line_terminator=os.linesep,
            )
            header = f.split('_')[-4]
            all_means = mean_bold_df.mean(axis=1)
            all_means.to_csv(
                f.replace("normalized_ts", "mean_norm_bold_response"),
                mode="w",
                header=[header],
                index=False,
                line_terminator=os.linesep,
            )

    def run(self):
        ts_files = self.get_ts_file(path=self.path)
        self.calc_ts_properties(ts_files=ts_files)
        self.calculate_subjects_mean_bold(path=self.path)

    # def trial(self):
    #     rel_mean = scaled_mean[1:41]
    #     non_norm_mean = s.mean(axis=1)[1:41]
    #     skip = 10
    #     norm_BOLD = list()
    #     non_norm_BOLD = list()
    #     j = 0
    #     for i in range(4):
    #         norm_BOLD.append(rel_mean[j: j + skip])
    #         non_norm_BOLD.append(non_norm_mean[j: j + skip])
    #         j += skip
    #     norm_BOLD = np.array(norm_BOLD)
    #     mean_norm_BOLD = norm_BOLD.mean(axis=0)
    #     pd.DataFrame(mean_norm_BOLD).to_csv(
    #         all_subjects_norm_bold,
    #         mode="w",
    #         index=False,
    #         line_terminator=os.linesep,
    #     )

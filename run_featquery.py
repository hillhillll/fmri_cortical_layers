import glob
import os
import subprocess
from bash_cmd import bash_get

###


class Featquery:
    def __init__(self, path: str = r"C:/Users/Owner/Desktop/fsl_pipeline_trial"):
        self.path = r"{0}/derivatives/feats".format(path)
        self.subjects = glob.glob("{0}/*".format(self.path))

    def query(self, path: str, subjects: list):
        for subj in subjects:
            subnum = subj.split(os.sep)[-1]
            if not os.path.isdir(
                "{0}/tsplots/{1}".format(os.path.dirname(path), subnum)
            ):
                os.makedirs("{0}/tsplots/{1}".format(os.path.dirname(path), subnum))
            feats = glob.glob("{0}/*.feat".format(subj))
            for feat in feats:
                prot = (
                    feat.split(os.sep)[-1]
                    .split(".")[0]
                    .replace("{0}_".format(subnum), "")
                )
                mask = glob.glob("{0}/*_bin.nii.gz".format(feat))[0]
                output = "{0}/tsplots/{1}/{2}".format(
                    os.path.dirname(path), subnum, prot
                )
                if os.path.isdir(output):
                    print(
                        "{0} already went through featquery ROI analysis".format(subnum)
                    )
                else:
                    print("Analyzing {0} using featquery".format(subnum))
                    cmd = bash_get(
                        '-lc "featquery 1 {0} 1 stats/cope1 {1} -p -s -b {2}"'.format(
                            feat.replace(feat[0:2], "/mnt/" + feat[0].lower()),
                            prot.replace(feat[0:2], "/mnt/" + feat[0].lower()),
                            mask.replace(feat[0:2], "/mnt/" + feat[0].lower()),
                        )
                    )
                    subprocess.run(cmd)
                    if os.path.isdir(output):
                        os.remove(output)
                    os.rename("{0}/{1}".format(feat, prot), output)

    def run(self):
        self.query(path=self.path, subjects=self.subjects)

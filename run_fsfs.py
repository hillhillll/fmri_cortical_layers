import os
import glob
import subprocess
from bash_cmd import bash_get


class run_all_fsfs:
    def __init__(self, path: str = r"C:/Users/Owner/Desktop/fsl_pipeline_trial"):
        self.path = r"{0}/Nifti".format(path)

    def declare_paths(self, path: str):
        fsfdir = r"{0}/derivatives/scripts/fsfs".format(os.path.dirname(path))
        feat_dir = "{0}/derivatives/feats".format(os.path.dirname(path))
        all_fsfs = glob.glob("{0}/lev1/*".format(fsfdir))
        return feat_dir, all_fsfs

    def run_fsfs(self, feat_dir: str, all_fsfs: list):
        for fsf in all_fsfs:
            cur_hdr = fsf.split(os.sep)[-1][:-4]
            cur_hdr = cur_hdr.replace("design_", "")
            sub = cur_hdr.split("_")[0]
            cur_feat = "{0}/{1}/{2}.feat".format(feat_dir, sub, cur_hdr)
            flag = "{0}/stats/smoothness".format(cur_feat)
            if not os.path.isfile(flag):
                print('Analyzing {0}'.format(cur_hdr))
                cmd = bash_get('-lc "feat {0}"'.format(fsf))
                subprocess.run(cmd)
                while os.path.isfile(flag) == False:
                    if os.path.isfile(flag) == True:
                        break
            else:
                print('Already analyzed {0}'.format(cur_hdr))

    def run(self):
        feat_dir, all_fsfs = self.declare_paths(path=self.path)
        self.run_fsfs(feat_dir=feat_dir, all_fsfs=all_fsfs)

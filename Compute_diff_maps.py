import glob
import os
import nibabel as nib
import numpy as np
np.seterr(divide='ignore', invalid='ignore')
PATH = os.path.abspath("C:/Users/Owner/Desktop/fsl_pipeline_trial")
ACTIONS = ["Motor", "Sensory"]


class Diff_compute:
    def __init__(self, path: str = PATH):
        self.path = r"{0}/derivatives/feats".format(path)

    def get_subject(self, path):
        subjects = glob.glob(r"{0}/sub-*".format(path))
        return subjects

    def get_subj_protocols(self, subj, action):
        protocols = glob.glob(r"{0}/*{1}*IREPITI*.feat".format(subj, action))
        return protocols

    def calc_norm_SE(self, subj, action):
        SE_img = glob.glob(
            r"{0}/*{1}*[SE-EPI|Gre]*.feat/stats/tstat1.nii.gz".format(subj, action)
        )[0]
        SE_img = nib.load(SE_img)
        raw_data = SE_img.get_data()
        norm_data = (raw_data - raw_data.min()) / (raw_data.max() - raw_data.min())
        return norm_data

    def calc_norm_IRSE(self, prot):
        IRSE_img = nib.load(r"{0}/stats/tstat1.nii.gz".format(prot))
        aff = IRSE_img.affine
        raw_data = IRSE_img.get_data()
        norm_data = (raw_data - raw_data.min()) / (raw_data.max() - raw_data.min())
        return norm_data, aff

    def calc_diff(self, SE_data, IRSE_data, aff):
        diff_img = np.zeros(SE_data.shape)
        locs = IRSE_data.shape
        diff_img[: locs[0], : locs[1], : locs[2]] = IRSE_data
        diff_img = SE_data - diff_img
        diff_img = (diff_img - diff_img.min()) / (diff_img.max() - diff_img.min())
        diff_img *= 100
        new_img = nib.Nifti1Image(diff_img, affine=aff)
        return new_img

    def run(self):
        subjects = self.get_subject(path=self.path)
        for subj in subjects:
            for action in ACTIONS:
                SE_data = self.calc_norm_SE(subj=subj, action=action)
                protocls = self.get_subj_protocols(subj=subj, action=action)
                for prot in protocls:
                    [IRSE_data, aff] = self.calc_norm_IRSE(prot=prot)
                    new_img = self.calc_diff(
                        SE_data=SE_data, IRSE_data=IRSE_data, aff=aff
                    )
                    nib.save(new_img, r"{0}/diff_img.nii.gz".format(prot))

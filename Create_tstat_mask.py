#%%
import nibabel as nib
import os
import glob

#%%
PATH = os.path.abspath(r"C:\Users\Owner\Desktop\Cortical_layers_fMRI")
CUT_OFF = 2.5


class Create_mask:
    def __init__(self, path: str = PATH, cut_off: float = CUT_OFF):
        self.high_lev_dir = r"{0}\derivatives\feats\High-lev".format(path)
        self.cut_off = cut_off

    def get_high_lev_feats(self, high_lev_dir: str):
        high_lev_feats = glob.glob(r"{0}/*.gfeat".format(high_lev_dir))
        return high_lev_feats

    def load_tstat_img(self, high_lev_feat: str):
        header = r"{0}/cope1.feat\stats\tstat1.nii.gz".format(high_lev_feat)
        tstat_img = nib.load(header)
        return tstat_img

    def create_mask(self, tstat_img, cut_off: float):
        mask = tstat_img.get_fdata()
        mask[mask <= cut_off] = 0
        mask[mask != 0] = 1
        mask_img = nib.Nifti1Image(mask, tstat_img.affine, tstat_img.header)
        return mask_img

    def save_mask(self, mask_img, high_lev_feat: str):
        new_file = r"{0}/tstat_mask.nii.gz".format(high_lev_feat)
        nib.save(mask_img, new_file)

    def run(self):
        high_lev_feats = self.get_high_lev_feats(high_lev_dir=self.high_lev_dir)
        for high_lev_feat in high_lev_feats:
            tstat_img = self.load_tstat_img(high_lev_feat=high_lev_feat)
            mask_img = self.create_mask(tstat_img=tstat_img, cut_off=self.cut_off)
            self.save_mask(mask_img=mask_img, high_lev_feat=high_lev_feat)

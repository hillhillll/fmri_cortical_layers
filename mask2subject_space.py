#%%
import bash_cmd
import os
from nipype.interfaces import fsl
import glob
from colorama import Fore, Back, Style

#%%
PATH = os.path.abspath(r"C:\Users\Owner\Desktop\Cortical_layers_fMRI")
ACTIONS = ["Motor", "Sensory"]


class Generate_masks:
    def __init__(self, path: str = PATH):
        self.path = path
        self.feat_dir = r"{0}/derivatives\feats".format(self.path)
        self.actions = ACTIONS

    def get_original_mask(self, feat_dir, action):
        original_mask = glob.glob(
            r"{0}/high_lev/{1}*.gfeat/tstat_mask.nii.gz".format(feat_dir, action)
        )[0]
        return original_mask

    def get_subjects(self, feat_dir):
        subjects = glob.glob(r"{0}/sub-*".format(feat_dir))
        return subjects

    def get_highres_img(self, subj: str):
        subj_feat = glob.glob(r"{0}/*SE-EPI*/reg".format(subj))
        highres = r"{0}/highres.nii.gz".format(subj_feat[0])
        return highres

    def get_func_images(self, subj: str):
        funcs = glob.glob(r"{0}/*.feat/reg/example_func.nii.gz".format(subj))
        return funcs

    def FLT_mask2highres(self, mask, highres, subj, action):
        print(Back.BLACK, Fore.RED)
        print("Linear registration from mask to highres template...")
        print(Style.RESET_ALL)
        if not os.path.isfile(r"{0}/{1}_mask2highres_linear.mat".format(subj, action)):
            applyxfm = fsl.ApplyXFM()
            applyxfm.inputs.in_file = mask
            applyxfm.inputs.reference = highres
            applyxfm.inputs.in_matrix_file = r"{0}\standard2highres.mat".format(
                os.path.dirname(highres)
            )
            applyxfm.inputs.out_matrix_file = r"{0}/{1}_mask2highres_linear.mat".format(
                subj, action
            )
            applyxfm.inputs.out_file = r"{0}/{1}_mask2highres_linear.nii.gz".format(
                subj, action
            )
            cmd = "{0}".format(applyxfm.cmdline)
            cmd = bash_cmd.Get_nipype_cmd(cmd)
            os.system(cmd)
            return applyxfm.inputs.out_matrix_file
        else:
            return r"{0}/{1}_mask2highres_linear.mat".format(subj, action)

    def FNT_mask2highres(self, mask, highres, subj, aff, action):
        print(Back.BLACK, Fore.RED)
        print("Non-linear registration from mask to highres template...")
        print(Style.RESET_ALL)
        if not os.path.isfile(r"{0}/{1}_mask2subj_highres.nii.gz".format(subj, action)):
            fnt = fsl.FNIRT()
            fnt.inputs.affine_file = aff
            fnt.inputs.ref_file = highres
            fnt.inputs.in_file = mask
            fnt.inputs.warped_file = r"{0}/{1}_mask2subj_highres.nii.gz".format(
                subj, action
            )
            cmd = bash_cmd.Get_nipype_cmd(fnt.cmdline)
            res = os.system(cmd)
            return fnt.inputs.warped_file
        else:
            return r"{0}/{1}_mask2subj_highres.nii.gz".format(subj, action)

    def FLT_warped_mask2example_func(self, warped_mask, func, action):
        print(Back.BLACK, Fore.RED)
        print(
            "Linear registration from highres-spaced mask to example_func template..."
        )
        print(Style.RESET_ALL)
        if not os.path.isfile(
            r"{0}/{1}_mask2example_func.nii.gz".format(
                os.path.dirname(os.path.dirname(func)), action
            )
        ):
            applyxfm = fsl.ApplyXFM()
            applyxfm.inputs.in_file = warped_mask
            applyxfm.inputs.reference = func
            applyxfm.inputs.in_matrix_file = r"{0}\highres2example_func.mat".format(
                os.path.dirname(func)
            )
            applyxfm.inputs.out_file = r"{0}/{1}_mask2example_func.nii.gz".format(
                os.path.dirname(os.path.dirname(func)), action
            )
            cmd = "{0}".format(applyxfm.cmdline)
            cmd = bash_cmd.Get_nipype_cmd(cmd)
            os.system(cmd)

    def run(self):
        subjects = self.get_subjects(feat_dir=self.feat_dir)
        for subj in subjects:
            print(Back.GREEN, Fore.RED)
            print("Woring on {0}".format(subj.split(os.sep)[-1]))
            print(Style.RESET_ALL)
            highres = self.get_highres_img(subj=subj)
            for action in self.actions:
                mask = self.get_original_mask(feat_dir=self.feat_dir, action=action)
                aff = self.FLT_mask2highres(
                    mask=mask, highres=highres, subj=subj, action=action
                )
                warped_mask = self.FNT_mask2highres(
                    mask=mask, highres=highres, subj=subj, aff=aff, action=action
                )
                funcs = self.get_func_images(subj=subj)
                for func in funcs:
                    self.FLT_warped_mask2example_func(
                        warped_mask=warped_mask, func=func, action=action
                    )


#%%
# import nibabel as nib
# import matplotlib.pyplot as plt
# img = nib.load(mask)
# data = img.get_fdata()
# slice_0 = data[45, :, :]
# slice_1 = data[:, 50, :]
# slice_2 = data[:, :, 45]
# def show_slices(slices):
#     """ Function to display row of image slices """
#     fig, axes = plt.subplots(1, len(slices))
#     for i, slice in enumerate(slices):
#         axes[i].imshow(slice.T, cmap="hot", origin="lower")
# # show_slices([slice_0,slice_1,slice_2])

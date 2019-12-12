import bash_cmd
import os
import glob
import numpy as np
import pandas as pd
import nibabel as nib
from colorama import Fore, Back, Style

#%%
PATH = os.path.abspath(r"C:\Users\Owner\Desktop\Cortical_layers_fMRI")
ACTIONS = ["Motor", "Sensory"]
TIS = np.arange(630,751,20)

class Calc_TI_map:
    def __init__(self, path: str = PATH):
        self.path = path
        self.feat_dir = r"{0}/derivatives\feats".format(self.path)
        self.actions = ACTIONS

    def get_subjects(self, feat_dir: str):
        subjects = glob.glob(r"{0}/sub-*".format(feat_dir))
        return subjects

    def get_func_images(self, subj: str):
        funcs = glob.glob(r"{0}/*.feat/filtered_func_data.nii.gz".format(subj))
        return funcs

    def load_func_data(self, func):
        func_img = nib.load(func)
        return func_img

    def load_mask_data(self, func: str, action):
        mask_img = nib.load(
            r"{0}/{1}_mask2example_func.nii.gz".format(os.path.dirname(func), action)
        )
        # mask = mask_img.get_fdata()
        return mask_img

    def gen_prot_TI_map(self, func, action):
        mask_img = self.load_mask_data(func=func, action=action)
        mask = mask_img.get_fdata()
        func_img = self.load_func_data(func=func)
        x_y_z = mask.shape
        TI_map = np.zeros(x_y_z)
        func_data = func_img.get_fdata()
        for x in range(x_y_z[0]):
            for y in range(x_y_z[1]):
                for z in range(x_y_z[2]):
                    if mask[x, y, z] != 0:
                        TC = func_data[x, y, z]
                        if TC.nonzero()[0].size > 0:
                            relevant = TC[4:44]
                            mean_bold = self.calc_mean_bold(relevant=relevant)
                            peak_value = mean_bold.values[3:7].mean()
                            # peak_value = mean_bold.max() - mean_bold.min()
                            TI_map[x, y, z] = peak_value
        TI_img = nib.Nifti1Image(TI_map, affine=mask_img.affine, header=mask_img.header)
        new_file = r"{0}/{1}_peak_BOLD_map.nii.gz".format(os.path.dirname(func), action)
        nib.save(TI_img, new_file)

    def calc_mean_bold(self, relevant):
        BOLD_duration = 10
        iterables = [
            ["First", "Second", "Third", "Fourth"],
            np.arange(BOLD_duration).tolist(),
        ]
        index = pd.MultiIndex.from_product(iterables, names=["Action", "Time"])
        mean_bold_df = pd.DataFrame(relevant, index=index)
        mean_bold_df = mean_bold_df.mean(level="Time")
        return mean_bold_df

    def gen_TI_maps(self):
        subjects = self.get_subjects(feat_dir=self.feat_dir)
        for subj in subjects:
            print(Back.BLACK, Fore.RED)
            print("working on {0}...".format(subj.split(os.sep)[-1]))
            print(Style.RESET_ALL)
            funcs = self.get_func_images(subj=subj)
            for action in self.actions:
                for func in funcs:
                    self.gen_prot_TI_map(func=func, action=action)

    def calc_subj_TI_map(self):
        subjects = self.get_subjects(feat_dir=self.feat_dir)
        for subj in subjects:
            for action in self.actions:
                TI_init_map = self.get_IR_map(subj=subj,TI='630',action = action)
                x_y_z = TI_init_map.shape
                size_of_map = (x_y_z[0],x_y_z[1],x_y_z[2],len(TIS))
                TI_map = np.zeros(size_of_map)
                TI_min_map = np.zeros(size_of_map[0:-1])
                for i in range(len(TIS)):
                    TI = TIS[i]
                    action_map = self.get_IR_map(subj=subj,TI=TI,action=action)
                    TI_data = action_map.get_fdata()
                    TI_map[:,:,:,i] = TI_data
                for x in range(x_y_z[0]):
                    for y in range(x_y_z[1]):
                        for z in range(x_y_z[2]):
                            TI_num = TI_map[x,y,z,:].argmin()
                            TI_min_map[x,y,z] = TIS[TI_num]
                TI_min_map_nii = nib.Nifti1Image(TI_min_map,affine=TI_init_map.affine,header=TI_init_map.header)
                nib.save(TI_min_map_nii,r'{0}/{1}_TI_map.nii.gz'.format(subj,action))


    def get_IR_map(self,subj:str,TI,action):
        TI_map =glob.glob(r'{0}/*{1}*{2}*.feat/{1}_peak_BOLD_map.nii.gz'.format(subj,action,TI))[0]
        TI_map = nib.load(TI_map)
        return TI_map

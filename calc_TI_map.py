import bash_cmd
import os
import glob
import numpy as np
import pandas as pd
import nibabel as nib
from nipype.interfaces import fsl
from colorama import Fore, Back, Style

#%%
PATH = os.path.abspath(r"C:\Users\Owner\Desktop\Cortical_layers_fMRI")
ACTIONS = ["Motor", "Sensory"]
TIS = np.arange(630, 751, 20)


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
        """
        Calculate peak-BOLD map for each subject and for each task
        :param func: filtered_func_data.nii.gz 4-D functional image
        :param action: 'Motor' or 'Sensory'
        :return:
        """
        mask_img = self.load_mask_data(func=func, action=action)
        mask = mask_img.get_fdata()
        func_img = self.load_func_data(func=func)
        x_y_z = mask.shape
        TI_map = np.zeros(x_y_z)
        func_data = func_img.get_fdata()
        func_data = (
            (func_data - func_data.min()) / (func_data.max() - func_data.min())
        ) * 100
        for x in range(x_y_z[0]):
            for y in range(x_y_z[1]):
                for z in range(x_y_z[2]):
                    if mask[x, y, z] != 0:
                        TC = func_data[x, y, z]
                        if TC.nonzero()[0].size > 0:
                            relevant = TC[4:44]
                            mean_bold = self.calc_mean_bold(relevant=relevant)
                            peak_value = mean_bold.values[3:7].mean() - mean_bold.min()
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

    def calc_subj_TI_maps(self):
        subjects = self.get_subjects(feat_dir=self.feat_dir)
        for subj in subjects:  # Go through each subject
            if not os.path.isdir(r"{0}/TI_maps".format(subj)):
                os.mkdir(r"{0}/TI_maps".format(subj))  # Create TI maps dir
            for mask in self.actions:
                if not os.path.isdir(r"{0}/TI_maps/{1}_mask".format(subj, mask)):
                    os.mkdir(r"{0}/TI_maps/{1}_mask".format(subj, mask))
                for task in self.actions:
                    if not os.path.isdir(
                        r"{0}/TI_maps/{1}_mask/{2}_task".format(subj, mask, task)
                    ):
                        os.mkdir(
                            r"{0}/TI_maps/{1}_mask/{2}_task".format(subj, mask, task)
                        )
                    TI_init_map = self.initiate_map(subj=subj, action=mask)
                    x_y_z = TI_init_map.shape
                    size_of_map = (x_y_z[0], x_y_z[1], x_y_z[2], len(TIS))
                    TI_map = np.zeros(size_of_map)
                    TI_min_map = np.zeros(size_of_map[0:-1])
                    for i in range(len(TIS)):
                        TI = TIS[i]
                        # this_feat = glob.glob(
                        #     r"{0}/*{1}*{2}*.feat".format(subj, task, TI)
                        # )[0]
                        # this_map = nib.load(
                        #     r"{0}/reg/task-{1}_mask-{2}_peak_BOLD_map2highres.nii.gz".format(
                        #         this_feat, task, mask
                        #     )
                        # )
                        # this_map = self.TI_mask2highres(
                        #     subj=subj, TI=TI, task=task, mask=mask
                        # )
                        this_map = glob.glob(
                            r"{0}/*{1}*{2}*.feat/{3}_peak_BOLD_map.nii.gz".format(
                                subj, task, TI, mask
                            )
                        )[0]
                        this_map = nib.load(this_map)
                        TI_data = this_map.get_fdata()
                        TI_map[:, :, :, i] = TI_data
                    for x in range(x_y_z[0]):
                        for y in range(x_y_z[1]):
                            for z in range(x_y_z[2]):
                                TI_num = TI_map[x, y, z, :].argmin()
                                TI_min_map[x, y, z] = TIS[TI_num]
                    TI_min_map_nii = nib.Nifti1Image(
                        TI_min_map, affine=this_map.affine, header=this_map.header
                    )
                    nib.save(
                        TI_min_map_nii,
                        r"{0}/TI_maps/{1}_mask/{2}_task/Combined_TI_map.nii.gz".format(
                            subj, mask, task
                        ),
                    )
                    self.calc_each_TI_map(
                        TI_min_map=TI_min_map_nii, subj=subj, task=task, mask=mask
                    )
        self.fix_630()

    def fix_630(self):
        subjects = self.get_subjects(feat_dir=self.feat_dir)
        for subj in subjects:
            for mask in self.actions:
                for task in self.actions:
                    this_630 = glob.glob(
                        r"{0}/TI_maps/{1}_mask/{2}_task/630*".format(subj, mask, task)
                    )[0]
                    this_combined = glob.glob(
                        r"{0}/TI_maps/{1}_mask/{2}_task/combined*".format(
                            subj, mask, task
                        )
                    )[0]
                    mask_img = glob.glob(
                        r"{0}/*task-{1}_acq-IREPITI630*.feat/{2}_peak_BOLD_map.nii.gz".format(
                            subj, task, mask
                        )
                    )[0]
                    mask_data = nib.load(mask_img).get_fdata()
                    map_630 = nib.load(this_630)
                    map_630_data = map_630.get_fdata()
                    map_combined = nib.load(this_combined)
                    map_combined_data = map_combined.get_fdata()
                    for x in range(map_630_data.shape[0]):
                        for y in range(map_630_data.shape[1]):
                            for z in range(map_630_data.shape[2]):
                                # map_630_data[x, y, z] = 0
                                if mask_data[x, y, z] == 0:
                                    map_combined_data[x, y, z] = 0
                                    # map_630_data[x, y, z] = 0
                                if (
                                    map_combined_data[x, y, z] == 630
                                    and mask_data[x, y, z] != 0
                                ):
                                    map_630_data[x, y, z] = 1
                                else:
                                    map_630_data[x, y, z] = 0
                                # if (
                                #     map_630_data[x, y, z] == 0
                                #     and map_combined_data[x, y, z] == 630
                                # ):
                                #     map_combined_data[x, y, z] = 0
                    map_630_nii = nib.Nifti1Image(
                        map_630_data, affine=map_630.affine, header=map_630.header
                    )
                    nib.save(map_630_nii, this_630)
                    map_combined_nii = nib.Nifti1Image(
                        map_combined_data,
                        affine=map_combined.affine,
                        header=map_combined.header,
                    )
                    nib.save(map_combined_nii, this_combined)

    def calc_each_TI_map(self, TI_min_map, subj, task, mask):
        data = TI_min_map.get_fdata()
        x_y_z = data.shape
        for i in range(len(TIS)):
            TI = TIS[i]
            TI_map = np.zeros(x_y_z)
            for x in range(x_y_z[0]):
                for y in range(x_y_z[1]):
                    for z in range(x_y_z[2]):
                        if data[x, y, z] == TI:
                            TI_map[x, y, z] = 1
            TI_map_nii = nib.Nifti1Image(
                TI_map, affine=TI_min_map.affine, header=TI_min_map.header
            )
            nib.save(
                TI_map_nii,
                r"{0}/TI_maps/{1}_mask/{2}_task/{3}_map.nii.gz".format(
                    subj, mask, task, str(TI)
                ),
            )

    def initiate_map(self, subj, action):
        reg_map = glob.glob(
            r"{0}/*{1}*630*.feat/{1}_peak_BOLD_map.nii.gz".format(subj, action)
        )[0]
        TI_map = nib.load(reg_map)
        return TI_map

    def masks2highres(self):
        subjects = self.get_subjects(feat_dir=self.feat_dir)
        for subj in subjects:
            for task in self.actions:
                for mask in self.actions:
                    for i in range(len(TIS)):
                        TI_map = self.TI_mask2highres(
                            subj=subj, TI=str(TIS[i]), task=task, mask=mask
                        )

    def TI_mask2highres(self, subj: str, TI, task, mask):
        TI_map = glob.glob(
            r"{0}/*{1}*{2}*.feat/{3}_peak_BOLD_map.nii.gz".format(subj, task, TI, mask)
        )[0]
        flt = fsl.FLIRT()
        flt.inputs.in_file = TI_map
        flt.inputs.reference = r"{0}/reg/highres.nii.gz".format(os.path.dirname(TI_map))
        flt.inputs.in_matrix_file = r"{0}\reg/example_func2highres.mat".format(
            os.path.dirname(TI_map)
        )
        flt.inputs.out_file = r"{0}/reg/task-{1}_mask-{2}_peak_BOLD_map2highres.nii.gz".format(
            os.path.dirname(TI_map), task, mask
        )
        cmd = "{0}".format(flt.cmdline)
        cmd = bash_cmd.Get_nipype_cmd(cmd)
        os.system(cmd)

        TI_map = nib.load(flt.inputs.out_file)
        print(flt.inputs.out_file)
        return TI_map

    def get_func2standard(self, subj, task, TI):
        aff = glob.glob(
            r"{0}/*task-{1}_acq-IREPITI{2}*.feat/reg/example_func2standard.mat".format(
                subj, task, TI
            )
        )[0]
        ref = glob.glob(
            r"{0}/*task-{1}_acq-IREPITI{2}*.feat/reg/standard.nii.gz".format(
                subj, task, TI
            )
        )[0]
        return aff, ref

    def TI_map2standard_lin(self, TI_map, aff, ref, out_file):
        print(Back.BLACK, Fore.RED)
        print("Linear registration from TI_map to standard template...")
        print(Style.RESET_ALL)
        options = r"-bins 256 -cost corratio -searchrx -90 90 -searchry -90 90 -searchrz -90 90 -dof 12 -interp trilinear"
        applyxfm = fsl.ApplyXFM()
        applyxfm.inputs.in_file = TI_map
        applyxfm.inputs.no_resample_blur = True
        applyxfm.inputs.no_resample = True
        applyxfm.inputs.reference = r"{0}/standard.nii.gz".format(os.path.dirname(aff))
        applyxfm.inputs.in_matrix_file = aff
        applyxfm.inputs.out_file = out_file
        cmd = "{0}".format(applyxfm.cmdline)
        cmd = bash_cmd.Get_nipype_cmd(cmd)
        os.system(cmd)

    def TI_maps2standard(self):
        subjects = self.get_subjects(feat_dir=self.feat_dir)
        for subj in subjects:
            print(Back.BLACK, Fore.RED)
            print("working on {0}...".format(subj.split(os.sep)[-1]))
            print(Style.RESET_ALL)
            # aff, warp = self.get_highres2standard(subj=subj)
            for mask in self.actions:
                for task in self.actions:
                    for i in range(len(TIS)):
                        TI = TIS[i]
                        aff, ref = self.get_func2standard(
                            subj=subj, task=task, TI=str(TI)
                        )
                        TI_map = glob.glob(
                            r"{0}/TI_maps/{1}_mask/{2}_task/{3}*.nii.gz".format(
                                subj, mask, task, str(TI)
                            )
                        )[0]
                        new_dir = os.path.dirname(TI_map).replace(
                            "TI_maps", "Normalized_TI_maps"
                        )
                        if not os.path.isdir(new_dir):
                            os.makedirs(new_dir)
                        reg_TI_map = TI_map.replace("TI_maps", "Normalized_TI_maps")
                        reg_TI_map = reg_TI_map.replace(".nii.gz", "2standard.nii.gz")
                        # mask2highres_aff = glob.glob(
                        #     r"{0}/*{1}*{2}*.feat/reg/example_func2highres.mat".format(
                        #         subj, task, str(TI)
                        #     )
                        # )[0]
                        # self.TI_map2highres_lin(
                        #     in_file=TI_map,
                        #     aff=mask2highres_aff,
                        #     out_file=mask2highres_out_file,
                        # )
                        # lin_TI_map = lin_TI_map.replace(
                        #     ".nii.gz", "2standard_lin.nii.gz"
                        # )
                        print(Back.BLACK, Fore.RED)
                        print("Linear registration...")
                        print(Style.RESET_ALL)
                        self.TI_map2standard_lin(
                            TI_map=TI_map, aff=aff, ref=ref, out_file=reg_TI_map
                        )
                        print(Back.BLACK, Fore.RED)
                        print("Done!")
                        # print(Style.RESET_ALL)
                        # print(Back.BLACK, Fore.RED)
                        # print("Non linear registration...")
                        # print(Style.RESET_ALL)
                        # nonlin_TI_map = lin_TI_map.replace("lin", "warped")
                        # self.TI_map2standard_nonlin(
                        #     TI_map=mask2highres_out_file,
                        #     warp=warp,
                        #     out_file=nonlin_TI_map,
                        # )
                        # print(Back.BLACK, Fore.RED)
                        # print("Done!")
                        # print(Style.RESET_ALL)

    def TI_map2standard_nonlin(self, TI_map, warp, out_file):
        print(Back.BLACK, Fore.RED)
        print("Non-linear registration from TI_map to standard template...")
        print(Style.RESET_ALL)
        if not os.path.isfile(out_file):
            fnt = fsl.FNIRT()
            fnt.inputs.inwarp_file = warp
            fnt.inputs.ref_file = r"{0}/standard.nii.gz".format(os.path.dirname(warp))
            fnt.inputs.in_file = TI_map
            fnt.inputs.warp_resolution = (6, 6, 6)
            fnt.inputs.warped_file = out_file
            cmd = bash_cmd.Get_nipype_cmd(fnt.cmdline)
            res = os.system(cmd)

    def TI_map2highres_lin(self, in_file, aff, out_file):
        print(Back.BLACK, Fore.RED)
        print(
            "Linear registration from TI_map in functional space to highres template..."
        )
        print(Style.RESET_ALL)
        # options = r"-bins 256 -cost corratio -searchrx -90 90 -searchry -90 90 -searchrz -90 90 -dof 7 -interp trilinear"
        applyxfm = fsl.ApplyXFM()
        applyxfm.inputs.in_file = in_file
        applyxfm.inputs.reference = r"{0}/highres.nii.gz".format(os.path.dirname(aff))
        applyxfm.inputs.in_matrix_file = aff
        applyxfm.inputs.out_file = out_file
        cmd = "{0}".format(applyxfm.cmdline)
        cmd = bash_cmd.Get_nipype_cmd(cmd)
        os.system(cmd)

    def clean_standard_TI_maps(self):
        subjects = self.get_subjects(feat_dir=self.feat_dir)
        standard_mask = glob.glob(
            r"{0}/*.feat/reg/standard_mask.nii.gz".format(subjects[0])
        )[0]
        for subj in subjects:
            standard_TI_maps = glob.glob(
                r"{0}/Normalized_TI_maps/*/*/*warped.nii.gz".format(subj)
            )
            for TI_map in standard_TI_maps:
                applymask = fsl.ApplyMask()
                applymask.inputs.in_file = TI_map
                applymask.inputs.mask_file = standard_mask
                applymask.inputs.out_file = TI_map
                cmd = "{0}".format(applymask.cmdline)
                cmd = bash_cmd.Get_nipype_cmd(cmd)
                os.system(cmd)

    def calc_mean_TI_maps(self):
        for i in range(len(TIS)):
            TI = TIS[i]
            mother_dir = r"{0}/TI_maps".format(os.path.dirname(self.feat_dir))
            for mask in self.actions:
                for task in self.actions:
                    new_dir = r"{0}/{1}_mask/{2}_task".format(mother_dir, mask, task)
                    if not os.path.isdir(new_dir):
                        os.makedirs(new_dir)
                    TI_maps = glob.glob(
                        r"{0}/sub-*/Normalized_TI_maps/{1}_mask/{2}_task/{3}*2standard.nii.gz".format(
                            self.feat_dir, mask, task, str(TI)
                        )
                    )
                    init_map = nib.load(TI_maps[0])
                    x_y_z = init_map.shape
                    map_size = (x_y_z[0], x_y_z[1], x_y_z[2], len(TI_maps))
                    this_map = np.zeros(map_size)
                    for j in range(len(TI_maps)):
                        subj_map = nib.load(TI_maps[j]).get_fdata()
                        subj_map[subj_map != 0] = TI
                        this_map[:, :, :, j] = subj_map
                    this_map = this_map.mean(axis=3)
                    this_map = (
                        (this_map - this_map.min()) / (this_map.max() - this_map.min())
                    ) * 100
                    # this_map[this_map != TI] = 0
                    this_map_nii = nib.Nifti1Image(
                        this_map, affine=init_map.affine, header=init_map.header
                    )
                    nib.save(
                        this_map_nii,
                        r"{0}/TI-{1}_mean_standard_map.nii.gz".format(new_dir, str(TI)),
                    )

    def calc_combined_norm_maps(self):
        mother_dir = r"{0}/TI_maps".format(os.path.dirname(self.feat_dir))
        for mask in self.actions:
            for task in self.actions:
                this_dir = r"{0}/{1}_mask/{2}_task".format(mother_dir, mask, task)
                TI_maps = glob.glob(r"{0}/*standard_map.nii.gz".format(this_dir))
                TI_maps.sort()
                init_map = nib.load(TI_maps[0])
                x_y_z = init_map.shape
                combined_map = np.zeros(x_y_z)
                map_size = (x_y_z[0], x_y_z[1], x_y_z[2], len(TI_maps))
                this_map = np.zeros(map_size)
                for i in range(len(TIS)):
                    TI_map = nib.load(TI_maps[i]).get_fdata()
                    this_map[:, :, :, i] = TI_map
                for x in range(x_y_z[0]):
                    for y in range(x_y_z[1]):
                        for z in range(x_y_z[2]):
                            vox_data = this_map[x, y, z, :]
                            combined_map[x, y, z] = TIS[vox_data.argmax()]
                combined_map_nii = nib.Nifti1Image(
                    combined_map, affine=init_map.affine, header=init_map.header
                )
                nib.save(
                    combined_map_nii, r"{0}/Combined_TI_map.nii.gz".format(this_dir)
                )

import os
import glob
import bash_cmd
from nipype.interfaces import fsl
from colorama import Fore, Back, Style

PATH = os.path.abspath("C:/Users/Owner/Desktop/Cortical_layers_fMRI")
ACTIONS = ["Motor", "Sensory"]


class Normalize:
    """
    There are 6 stages for normalization:
    2. FLIRT from low-res to MPRAGE (for .mat file)
    # 3. FLIRT from MPRAGE to low-res (based on inversed .mat file from (2))
    4. FLIRT from low-res-like MPRAGE scan to MNI template (for .mat file)
    5. FNIRT from low-res-like MPRAGE scan to MNI template (for .nii.gz field coefficient file)
    6. FNIRT from low-res to MNI template, based on .mat file from (5)
    """

    def __init__(self, path: str = PATH):
        self.path = r"{0}/derivatives/feats".format(path)
        self.actions = ACTIONS

    def get_subject(self, path):
        subjects = glob.glob(r"{0}/sub-*".format(path))
        return subjects

    def get_MPRAGE(self, subj):
        subj_feat = glob.glob(r"{0}/*SE-EPI*/reg".format(subj))
        MPRAGE = r"{0}/highres.nii.gz".format(subj_feat[0])
        return MPRAGE

    def get_protocols(self, subj):
        protocols = glob.glob(r"{0}/*.feat//example_func.nii.gz".format(subj))
        return protocols

    def BET(self, img: str):
        """
        BET brain extraction, from FSL
        :param img: path-like obj or string leading to whole-head image for brain extraction
        :return: brain-extracted image
        """
        btr = fsl.BET()
        prot_name = img.split(os.sep)[-2].split(".")[0]
        print(
            "{0} functional image is going through BET extraction...".format(prot_name)
        )
        btr.inputs.in_file = img
        if "SE-EPI" in img:
            btr.inputs.frac = 0.7
        else:
            btr.inputs.frac = 0.38
        btr.inputs.out_file = img.replace("_func", "_func_brain")
        cmd = bash_cmd.Get_nipype_cmd(btr.cmdline)
        res = os.system(cmd)
        return btr.inputs.out_file

    def get_IR_brains(self, subj, action):
        brains = glob.glob(r"{0}/*{1}*.feat//reg/example_func2highres.nii.gz".format(subj, action))
        return brains

    def get_SE_brains(self, subj, action):
        SE_img = glob.glob(
            r"{0}/*{1}*[SE-EPI|Gre]*.feat/example_func_brain.nii.gz".format(
                subj, action
            )
        )[0]
        return SE_img

    def FLIRT(self, img: str):
        flt = fsl.FLIRT()
        options = r"-bins 640 -cost corratio -searchrx -90 90 -searchry -90 90 -searchrz -90 90 -dof 9 -interp trilinear"
        flt.inputs.in_file = img
        flt.inputs.reference = r"{0}/reg/standard.nii.gz".format(os.path.dirname(img))
        flt.inputs.out_file = img.replace("example", "rexample")
        flt.inputs.out_matrix_file = img.replace(
            "example_func_brain.nii.gz", "rexample_func_brain.mat"
        )
        flt.inputs.output_type = "NIFTI_GZ"
        cmd = "{0} {1}".format(flt.cmdline, options)
        cmd = bash_cmd.Get_nipype_cmd(cmd)
        os.system(cmd)

    def FLT_lowres2MPRAGE(self, low_res, MPRAGE):
        """
        FLIRT linear registration from lowres brain scan to MPRAGE
        :param low_res: path-like obj or string leading to low-res functional image
        :param MPRAGE: path-like pbj or string leading to high-res structural image
        :return: BET_example_func2highres.mat affine file
        """
        applyxfm = fsl.ApplyXFM()
        applyxfm.inputs.in_file = low_res
        applyxfm.inputs.reference = MPRAGE
        applyxfm.inputs.in_matrix_file = r"{0}/reg/example_func2highres.mat".format(
            os.path.dirname(low_res)
        )
        applyxfm.inputs.out_file = r"{0}/reg/example_func_brain2highres.nii.gz".format(
            os.path.dirname(low_res)
        )
        cmd = "{0}".format(applyxfm.cmdline)
        cmd = bash_cmd.Get_nipype_cmd(cmd)
        os.system(cmd)
        # print("Extracting .mat affine file from low-res to high-res...")
        # flt = fsl.FLIRT()
        # # options = r"-bins 640 -cost corratio -searchrx -90 90 -searchry -90 90 -searchrz -90 90 -dof 9 -interp trilinear"
        # flt.inputs.in_file = low_res
        # flt.inputs.reference = MPRAGE
        # flt.inputs.out_file = low_res.replace(
        #     "example_func_brain", "reg/example_func_brain2highres"
        # )
        # # flt.inputs.out_matrix_file = low_res.replace(
        # #     "example_func.nii.gz", "reg/example_func2highres_head.mat"
        # # )
        # cmd = "{0} {1}".format(flt.cmdline, options)
        # cmd = bash_cmd.Get_nipype_cmd(cmd)
        # os.system(cmd)
        return applyxfm.inputs.out_file

    def FLT_tstat2MPRAGE(self, tstat, MPRAGE):

        applyxfm = fsl.ApplyXFM()
        applyxfm.inputs.in_file = tstat
        applyxfm.inputs.reference = MPRAGE
        applyxfm.inputs.in_matrix_file = r"{0}/reg/example_func2highres.mat".format(
            os.path.dirname(os.path.dirname(tstat))
        )
        applyxfm.inputs.out_file = r"{0}/reg/tstat2highres.nii.gz".format(
            os.path.dirname(os.path.dirname(tstat))
        )
        cmd = "{0}".format(applyxfm.cmdline)
        cmd = bash_cmd.Get_nipype_cmd(cmd)
        os.system(cmd)
        return applyxfm.inputs.out_file

    def applyXFM_FLIRT(self, tstat, MPRAGE, inv_aff):
        """
        Apply the inverted affine file from FLIRT procedure on MPRAGE scan to make it low-res-like
        :param low_res: low_res: path-like obj or string leading to low-res functional image
        :param MPRAGE: path-like pbj or string leading to high-res structural image
        :param inv_aff: inverted affine file
        :return: path-like pbj or string leading to high-res structural image in low-res space
        """
        print("FLIRT registration from high-res img to low-res")
        applyxfm = fsl.ApplyXFM()
        applyxfm.inputs.in_file = tstat
        applyxfm.inputs.reference = MPRAGE
        applyxfm.inputs.in_matrix_file = inv_aff
        applyxfm.inputs.out_matrix_file = tstat.replace(
            "stats/tstat1.nii.gz", "reg/tstat2highres.mat"
        )
        applyxfm.inputs.out_file = tstat.replace(
            "stats/tstat1.nii.gz", "tstat2highres.nii.gz"
        )
        cmd = "{0}".format(applyxfm.cmdline)
        cmd = bash_cmd.Get_nipype_cmd(cmd)
        os.system(cmd)
        return applyxfm.inputs.out_file

    def FLT_highres_head2mni(self, MPRAGE: str):
        """
        FLIRT from highres in lowres space to mni
        :param MPRAGE: highres head image
        :return: .mat affine file of linear registration
        """
        print(Back.BLACK, Fore.RED)
        print("FLIRT registration from high-res head image to MNI template...")
        print(Style.RESET_ALL)
        flt = fsl.FLIRT()
        options = r"-bins 640 -cost corratio -searchrx -90 90 -searchry -90 90 -searchrz -90 90 -dof 9 -interp trilinear"
        flt.inputs.in_file = MPRAGE
        flt.inputs.reference = r"{0}/standard_head.nii.gz".format(
            os.path.dirname(MPRAGE)
        )
        flt.inputs.out_file = MPRAGE.replace("highres_head", "highres_head2MNI")
        flt.inputs.out_matrix_file = MPRAGE.replace(
            "highres_head.nii.gz", "highres_head2MNI.mat"
        )
        flt.inputs.output_type = "NIFTI_GZ"
        cmd = "{0} {1}".format(flt.cmdline, options)
        cmd = bash_cmd.Get_nipype_cmd(cmd)
        os.system(cmd)
        return flt.inputs.out_matrix_file

    def FNIRT_low2mni(self, low_res: str):
        """
        FNIRT non-linear registration of low resolution file to MNI template, based on .mat affine file from FLIRT
        :param low_res: path-like obj or string leading to low-res functional image
        :param aff: .mat affine file of linear registration
        :return:
        """
        print(Back.BLACK, Fore.RED)
        print("FNIRT non-linear registration from low-res image to MNI template...")
        print(Style.RESET_ALL)
        fnt = fsl.FNIRT()
        # fnt.inputs.affine_file = aff
        fnt.inputs.ref_file = r"{0}/standard.nii.gz".format(os.path.dirname(low_res))
        fnt.inputs.inwarp_file = r"{0}/highres2standard_warp.nii.gz".format(
            os.path.dirname(low_res)
        )
        fnt.inputs.in_file = low_res
        fnt.inputs.warped_file = r"{0}/func_registered.nii.gz".format(
            os.path.dirname(os.path.dirname(low_res))
        )
        fnt.inputs.fieldcoeff_file = r"{0}/lowres_brain2standard_warp.nii.gz".format(
            os.path.dirname(low_res)
        )
        cmd = bash_cmd.Get_nipype_cmd(fnt.cmdline)
        res = os.system(cmd)
        return fnt.inputs.fieldcoeff_file

    def FNIRT_tstat2mni(self, tstat, coef):
        """
        FNIRT non-linear registration of low resolution file to MNI template, based on .mat affine file from FLIRT
        :param tstat: path-like obj or string leading to tstat activation image from FEAT
        :param aff: .mat affine file of linear registration
        :return:
        """
        print(Back.BLACK, Fore.RED)
        print("FNIRT non-linear registration from t-scores image to MNI template...")
        print(Style.RESET_ALL)
        aw = fsl.ApplyWarp()
        aw.inputs.in_file = tstat
        aw.inputs.ref_file = r"{0}/standard.nii.gz".format(os.path.dirname(tstat))
        aw.inputs.out_file = r"{0}/stats_registered.nii.gz".format(
            os.path.dirname(os.path.dirname(tstat))
        )
        aw.inputs.field_file = coef
        cmd = bash_cmd.Get_nipype_cmd(aw.cmdline)
        res = os.system(cmd)
        #
        # fnt = fsl.FNIRT()
        # # fnt.inputs.affine_file = aff
        # fnt.inputs.ref_file = r"{0}/reg/standard.nii.gz".format(
        #     os.path.dirname(tstat)
        # )
        # fnt.inputs.in_file = tstat
        # fnt.inputs.warped_file = r"{0}/tstat_normalized".format(os.path.dirname(tstat))
        # cmd = bash_cmd.Get_nipype_cmd(fnt.cmdline)
        # res = os.system(cmd)

    def run(self):
        subjects = self.get_subject(path=self.path)
        for subj in subjects:
            print(Back.BLACK, Fore.RED)
            print("Currently working on {0}".format(subj.split(os.sep)[-1]))
            print(Style.RESET_ALL)
            MPRAGE = self.get_MPRAGE(subj=subj)
            # aff = self.FLT_highres_head2mni(MPRAGE=MPRAGE)
            # print(
            #     "Done linear registration from high-res in low-res space to MNI standard space."
            # )
            for action in self.actions:
                protocols = self.get_IR_brains(subj=subj, action=action)
                for prot in protocols:
                    print(prot)
                    tstat = r'{0}/stats/tstat1.nii.gz'.format(os.path.dirname(os.path.dirname(prot)))
                    # func2highres = self.FLT_lowres2MPRAGE(
                    #     low_res=prot, MPRAGE=MPRAGE
                    # )
                    BET_prot = self.BET(prot)
                    print(Back.BLACK, Fore.RED)
                    print("FLIRT from brain-extracted func to highres done.")
                    print(Style.RESET_ALL)
                    coef = self.FNIRT_low2mni(low_res=BET_prot)
                    print(Back.BLACK, Fore.RED)
                    print(
                        "Finished non-linear registration of low-res image to MNI template."
                    )
                    print(Style.RESET_ALL)

                    # lowlike_highres = self.applyXFM_inverted_FLIRT(
                    #     low_res=prot, MPRAGE=MPRAGE, inv_aff=inv_aff
                    # )
                    # print("Done linear registration from high-res to low-res.")
                    # aff = self.FLT_lowlike2mni(lowlike_highres=lowlike_highres)
                    tstat_reg = self.FLT_tstat2MPRAGE(tstat=tstat, MPRAGE=MPRAGE)
                    print(Back.BLACK, Fore.RED)
                    print("Finished linear registration of tstat to highres")
                    self.FNIRT_tstat2mni(tstat=tstat_reg, coef=coef)
                    print(Style.RESET_ALL)

                    print(Back.BLACK, Fore.RED)
                    print(
                        "Finished non-linear registrationg of t-scores map to MNI remplate."
                    )
                    print(Style.RESET_ALL)


                    # print("BET done.")
                    # print(Style.RESET_ALL)

    # def normalize_tstat(self):
    #     subjects = self.get_subject(path=self.path)
    #     for subj in subjects:
    #         print("Currently working on {0}".format(subj.split(os.sep)[-1]))
    #         for action in self.actions:
    #             protocols = self.get_IR_brains(subj=subj, action=action)
    #             for prot in protocols:
    #                 tstat = prot.replace("example_func", "stats/tstat1")
    #                 aff = prot.replace(
    #                     "example_func.nii.gz", "/reg/example_func2standard.mat"
    #                 )
    #                 self.FNIRT_tstat2mni(tstat=tstat)

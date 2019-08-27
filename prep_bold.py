import glob
import os
import subprocess
from pathlib import Path
from bash_cmd import bash_get


PATH = Path("C:/Users/Owner/Desktop/Cortical_Layers_fMRI")


class RunPrepBold:
    def __init__(self, path: str = PATH):
        self.path = r"{0}/Nifti".format(path)
        self.OUTHTML = r"{0}/derivatives/scripts/bold_motion_QA.html".format(path)
        self.OUT_BAD_BOLD_LIST = r"{0}/derivatives/scripts/subs_lose_gt_45_vol_scrub.txt".format(
            path
        )
        self.bold_files = glob.glob("{0}/*/func/sub*.nii*".format(self.path))

    def check_existence(self, bold_file: str):
        func_dir = os.path.dirname(bold_file)
        sub = func_dir.split(os.sep)[-2]
        motion_assess_output = bold_file.split(os.sep)[-1].split("_")[1:3]
        motion_assess_output = "_".join(motion_assess_output)
        output_dir = os.sep.join([func_dir, "motion_assess", motion_assess_output])
        if os.path.isdir(output_dir):
            flag = False
            print(
                "Motion assessment for {0}`s {1} already done.".format(
                    sub, motion_assess_output
                )
            )
        else:
            flag = True
            print(
                "Calculating motion assessment for {0}`s {1}".format(
                    sub, motion_assess_output
                )
            )
        return flag

    def create_qas(self, outhtml: str, out_bad_bold_list: str):
        sub_dirs = glob.glob(r"{0}/sub-*/func".format(self.path))
        for this_dir in sub_dirs:
            if not os.path.isdir(r"{0}/motion_assess".format(this_dir)):
                os.mkdir(r"{0}/motion_assess".format(this_dir))
        if not os.path.isdir(os.path.dirname(outhtml)):
            os.makedirs(os.path.dirname(outhtml))
        if os.path.isfile(outhtml):
            os.remove(outhtml)
        if os.path.isfile(out_bad_bold_list):
            os.remove(out_bad_bold_list)

    def motion_assesment(self, outhtml: str, out_bad_bold_list: str, bold_files: list):
        for cur_bold in list(bold_files):
            flag = self.check_existence(cur_bold)
            bold_title = cur_bold.split(os.sep)
            # Store directory name
            cur_dir = os.path.dirname(cur_bold)
            # strip off .nii.gz from file name (makes code below easier)
            cur_bold_no_nii = cur_bold[:-4]
            m_a_dir = str(Path("{0}_motion_assess/".format(cur_bold_no_nii)))

            if flag:
                if os.path.isdir(m_a_dir) == False:
                    os.mkdir(m_a_dir)
                cmd = bash_get(
                    "-lc 'fsl_motion_outliers -i {0} -o {0}_motion_assess/confound.txt --fd --thresh=0.9 -p {0}_motion_assess/fd_plot -v > {0}_motion_assess/outlier_output.txt'".format(
                        cur_bold_no_nii
                    )
                )
                subprocess.run(cmd)
                # Put confound info into html file for review later on
                cmd = bash_get(
                    "-lc 'cat {0}_motion_assess/outlier_output.txt >> {1}'".format(
                        cur_bold_no_nii, outhtml
                    )
                )
                subprocess.run(cmd)
            # Last, if we're planning on modeling out scrubbed volumes later
            #   it is helpful to create an empty file if confound.txt isn't
            #   generated (i.e. no scrubbing needed).  It is basically a
            #   place holder to make future scripting easier
                con_f = Path("{0}_motion_assess/confound.txt".format(cur_bold_no_nii))
                if os.path.isfile(con_f) == False:
                    cmd = bash_get(
                        " -lc 'touch {0}_motion_assess/confound.txt'".format(
                            cur_bold_no_nii
                        )
                    )
                    subprocess.run(cmd)

            # Very last, create a list of subjects who exceed a threshold for
            #  number of scrubbed volumes.  This should be taken seriously.  If
            #  most of your scrubbed data are occurring during task, that's
            #  important to consider (e.g. subject with 20 volumes scrubbed
            #  during task is much worse off than subject with 20 volumes
            #  scrubbed during baseline.
            # These data have about 182 volumes and I'd hope to keep 140
            #  DO NOT USE 140 JUST BECAUSE I AM.  LOOK AT YOUR DATA AND
            #  COME TO AN AGREED VALUE WITH OTHER RESEARCHERS IN YOUR GROUP
                cmd = bash_get(
                    "-lc 'grep -o 1 {0}_motion_assess/confound.txt | wc -l'".format(
                        cur_bold_no_nii
                    )
                )
                output = subprocess.check_output(cmd)
                num_scrub = [int(s) for s in output.split() if s.isdigit()]
                if num_scrub[0] > 45:
                    with open(out_bad_bold_list, "a") as myfile:
                        myfile.write("{0}\n".format(cur_bold))
                if flag:
                    motion_assess_dir = "{0}_motion_assess".format(cur_bold_no_nii)
                    self.move_motion_assess_dirs(motion_assess_dir=motion_assess_dir)

    def move_motion_assess_dirs(self, motion_assess_dir: str):
        out_dir = r"{0}/motion_assess/{1}".format(
            os.path.dirname(motion_assess_dir),
            "_".join(motion_assess_dir.split("_")[-5:-3]),
        )
        os.rename(motion_assess_dir, out_dir)
    def run_qa(self):
        subjects_dirs = glob.glob(r'{0}/*'.format(self.path))
        for subdir in subjects_dirs:
            subj = subdir.split(os.sep)[-1]
            motion_assess = glob.glob(r'{0}/func/motion_assess/*'.format(subdir))
            for prot in motion_assess:
                file = open(self.OUTHTML, "a")
                file.write(
                    '<p>=============<p>FD plot {0} -- {1} <br><img src ="{2}/fd_plot.png" alt="FD Plot"></BODY></HTML>'.format(subj, prot.split(os.sep)[-1], prot)
                )
                file.close()
    def run(self):
        self.create_qas(outhtml=self.OUTHTML, out_bad_bold_list=self.OUT_BAD_BOLD_LIST)
        self.motion_assesment(
            outhtml=self.OUTHTML,
            out_bad_bold_list=self.OUT_BAD_BOLD_LIST,
            bold_files=self.bold_files,
        )
        self.run_qa()

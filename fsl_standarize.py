import glob
import subprocess
import bash_cmd
import os
from nipype.interfaces import fsl

class Prep_Fsl:
    def __init__(self, path: str = r"C:/Users/Owner/Desktop/fsl_pipeline_trial"):
        self.path = r"{0}/derivatives/feats".format(path)

    def FLIRT(self, path: str = None):
        if not path:
            path = self.path
        func_data = glob.glob(r"{0}/*/*.feat".format(path))
        for func in func_data:
            tstat = r"{0}/stats/tstat1.nii.gz".format(func)
            output_filtered_func = r"{0}/filtered_func_data_standard.nii.gz".format(
                func
            )
            outout_tstat = r"{0}/tstat1_standard.nii.gz".format(func)
            if os.path.isfile(output_filtered_func):
                print("Already standarized {0}".format(func.split(os.sep)[-1]))
            else:
                print("Standarizing {0}".format(func.split(os.sep)[-1]))
                standard2example = r"{0}/reg/example_func2standard.mat".format(func)
                cmd = bash_cmd.bash_get(
                    '-lc "flirt -in /usr/local/fsl/data/standard/MNI152_T1_2mm_brain -ref {0} -applyxfm -init {1} -out {2}"'.format(
                        filtered_func, standard2example, output_filtered_func
                    )
                )
                subprocess.run(cmd)
                cmd = bash_cmd.bash_get(
                    '-lc "flirt -in /usr/local/fsl/data/standard/MNI152_T1_2mm_brain -ref {0} -applyxfm -init {1} -out {2}"'.format(
                        tstat, standard2example, outout_tstat
                    )
                )
                subprocess.run(cmd)
                print(r"Finished standardizing {0}".format(func.split(os.sep)[-1]))

    def run(self):
        self.prep_filtered_func(path=self.path)
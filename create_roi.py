import os
import glob
import subprocess
from bash_cmd import bash_get

PATH = os.path.abspath("C:/Users/Owner/Desktop/Cortical_Layers_fMRI")
DEFAULT_MOTOR = {"x": 47, "y": 27, "z": 35}
DEFAULT_SENSORY = {"x": 45, "y": 25, "z": 36}
COORDINATES = {"motor": DEFAULT_MOTOR, "sensory": DEFAULT_SENSORY}


class CreateROI:
    def __init__(self, coordinates: dict = COORDINATES, path: str = PATH):
        self.path = "{0}/derivatives/feats".format(path)
        self.coordinates = coordinates

    def get_coordinates(self, file_path: str):
        if "Motor" in file_path:
            return self.coordinates["motor"]
        return self.coordinates["sensory"]

    def get_nifti_paths(self):
        return glob.glob(f"{self.path}/*/*.feat/filtered_func_data.nii.gz")

    def run(self):
        func_files = self.get_nifti_paths()
        for file_path in func_files:
            if "Motor" in file_path:
                out_point = "{0}/Motor_ROI_point".format(os.path.dirname(file_path))
                out_sphere = "{0}/Motor_ROI_sphere".format(os.path.dirname(file_path))
            elif "Sensory" in file_path:
                out_point = "{0}/Sensory_ROI_point".format(os.path.dirname(file_path))
                out_sphere = "{0}/Sensory_ROI_sphere".format(os.path.dirname(file_path))
            if os.path.isfile("{0}.nii.gz".format(out_sphere)):
                print(
                    "Already created ROI for {0}".format(
                        os.path.dirname(file_path).split(os.sep)[-1][:-5]
                    )
                )
            else:
                print(
                    "Creating ROI for {0}".format(
                        os.path.dirname(file_path).split(os.sep)[-1][:-5]
                    )
                )
                sphere_size = "8"
                if os.path.isfile("{0}.nii.gz".format(out_point)):
                    os.remove("{0}.nii.gz".format(out_point))
                coords = self.get_coordinates(file_path)
                if "IREPI" in file_path:
                    coords["z"] = str(float(coords["z"]) - 21)
                cmd = bash_get(
                    '-lc "fslmaths {0} -mul 0 -add 1 -roi {1} 1 {2} 1 {3} 1 0 1 {4} -odt float"'.format(
                        file_path, coords["x"], coords["y"], coords["z"], out_point
                    )
                )
                subprocess.run(cmd)
                while os.path.isfile("{0}.nii.gz".format(out_point)) == False:
                    print("Waiting on point")
                    if os.path.isfile("{0}.nii.gz".format(out_point)) == True:
                        break
                if os.path.isfile("{0}.nii.gz".format(out_sphere)) == True:
                    os.remove("{0}.nii.gz".format(out_sphere))
                cmd = bash_get(
                    '-lc "fslmaths {0} -kernel sphere {1} -fmean {2} -odt float"'.format(
                        out_point, sphere_size, out_sphere
                    )
                )
                subprocess.run(cmd)
                while os.path.isfile("{0}.nii.gz".format(out_sphere)) == False:
                    print("Waiting on Spehere")
                    if os.path.isfile("{0}.nii.gz".format(out_sphere)) == True:
                        break
                if os.path.isfile("{0}_bin.nii.gz".format(out_sphere)) == True:
                    os.remove("{0}_bin.nii.gz".format(out_sphere))
                cmd = bash_get(
                    '-lc "fslmaths {0}.nii.gz -bin {0}_bin.nii.gz"'.format(out_sphere)
                )
                subprocess.run(cmd)

import os
import glob
import subprocess
from bash_cmd import bash_get

# DEFAULT_SENSORY = {"x": 45, "y": 25, "z": 36}
# DEFAULT_MOTOR = {"x": 47, "y": 27, "z": 35}

PATH = os.path.abspath("C:/Users/Owner/Desktop/fsl_pipeline_trial")
DEFAULT_MOTOR = {"x": 45, "y": 27, "z": 35}
DEFAULT_SENSORY = {"x": 52, "y": 26, "z": 32}

COORDINATES = {"motor": DEFAULT_MOTOR, "sensory": DEFAULT_SENSORY}
TRUE_ROI = True


class CreateROI:
    def __init__(
        self,
        coordinates: dict = COORDINATES,
        path: str = PATH,
        true_roi: bool = TRUE_ROI,
    ):
        self.true_roi = true_roi
        self.path = "{0}/derivatives/feats".format(path)
        self.coordinates = coordinates

    def regenerate_dict(self):
        DEFAULT_MOTOR = {"x": 45, "y": 27, "z": 35}
        DEFAULT_SENSORY = {"x": 45, "y": 24, "z": 35}
        coordinates = {"motor": DEFAULT_MOTOR, "sensory": DEFAULT_SENSORY}
        return coordinates

    def generate_false_roi(self):
        DEFAULT_MOTOR = {"x": 37, "y": 7, "z": 22}
        DEFAULT_SENSORY = {"x": 37, "y": 7, "z": 22}
        coordinates = {"motor": DEFAULT_MOTOR, "sensory": DEFAULT_SENSORY}
        return coordinates

    def get_coordinates(self, file_path: str):
        if self.true_roi:
            self.coordinates = self.regenerate_dict()
        else:
            self.coordinates = self.generate_false_roi()
        if "Motor" in file_path:
            output = self.coordinates["motor"]
            return output
        else:
            output = self.coordinates["sensory"]
            return output

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
                sphere_size = "6"
                if os.path.isfile("{0}.nii.gz".format(out_point)):
                    os.remove("{0}.nii.gz".format(out_point))
                coords = self.get_coordinates(file_path)
                print(coords)
                if "IREPITI" in file_path:
                    coords["z"] = str(int(float(coords["z"]) - 21))
                cmd = bash_get(
                    '-lc "fslmaths {0} -mul 0 -add 1 -roi {1} 1 {2} 1 {3} 1 0 1 {4} -odt float"'.format(
                        file_path.replace(
                            file_path[0:2], "/mnt/" + file_path[0].lower()
                        ),
                        coords["x"],
                        coords["y"],
                        coords["z"],
                        out_point.replace(
                            out_point[0:2], "/mnt/" + file_path[0].lower()
                        ),
                    )
                )
                subprocess.run(cmd)
                if os.path.isfile("{0}.nii.gz".format(out_sphere)) == True:
                    os.remove("{0}.nii.gz".format(out_sphere))
                cmd = bash_get(
                    '-lc "fslmaths {0} -kernel sphere {1} -fmean {2} -odt float"'.format(
                        out_point.replace(
                            out_point[0:2], "/mnt/" + file_path[0].lower()
                        ),
                        sphere_size,
                        out_sphere.replace(
                            out_sphere[0:2], "/mnt/" + file_path[0].lower()
                        ),
                    )
                )
                subprocess.run(cmd)
                if os.path.isfile("{0}_bin.nii.gz".format(out_sphere)) == True:
                    os.remove("{0}_bin.nii.gz".format(out_sphere))
                cmd = bash_get(
                    '-lc "fslmaths {0}.nii.gz -bin {0}_bin.nii.gz"'.format(
                        out_sphere.replace(
                            out_sphere[0:2], "/mnt/" + file_path[0].lower()
                        )
                    )
                )
                subprocess.run(cmd)

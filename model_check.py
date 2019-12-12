import create_roi
import run_featquery
import gather_ts
import calc_ts_features
import export_excels
import plot_IR_3D
import plot_nullify
import os
import shutil
import glob

MODEL_CHECK_DIR = os.path.abspath(r"F:/Model_check")


class ModelCheck:
    """
    Running the last step of fsl_pipeline, using irrelevant ROI coordinates for ROI analysis
    """

    def __init__(self, ROI_name: str, path: str = MODEL_CHECK_DIR):
        self.path = path
        self.name = ROI_name

    def create_rois(self, path):
        """
        Create ROI for each FEAT directory, for further analysis
        :return: binary ROI spheres for motor and sensory paradigm, centered in voxel-based coordinates
        """
        rois = create_roi.CreateROI(path=path, true_roi=False)
        rois.run()

    def featquery(self, path):
        """
        ROI analysis based on featquery for each scan for which there is a ROI image in it's feat directory
        :param path: a string containing the path to the mother directory of all files
        :return: time series directory, containing the averaged time course in the relevant ROI
        """
        query = run_featquery.Featquery(path=path)
        query.run()

    def ts_gather(self, path: str = None):
        """
        Move all relevant averaged time courses and gather them in a specific time series directory
        :param path: a string containing the path to the mother directory of all files
        :return: time series directory, containing all averaged time courses, as extracted from featquery
        """

        gather = gather_ts.Get_TS(path=path)
        gather.run()

    def calc_ts_features(self, path: str = None):
        """
        Calculation of several features regarding the averaged time courses, creating the following files:

        all_ts = all raw-data time series from all subjects.
        fixed_ts = since an error occured while scanning 2 subjects (02 and 03), a realigned time series across all subjects.
        mean_bold_response = non-normalized, raw averaged bold response, across all subjects
        mean_norm_bold_response = after intra-subject normalization, a calculated mean normalized bold response.
        mean_ts = non-normalized, raw averaged time course, across all subjects
        mean_normalized_ts = a normalized time series across all subjects.
        normalized_ts = normalized time series for each subject.
        subjects_norm_BOLD_response = non-averaged, normalized BOLD response, for each subject.

        :param path: a string containing the path to the mother directory of all files
        :return: files mentioned above
        """

        features_calc = calc_ts_features.CalcMeanTS(path=path)
        features_calc.run()

    def plot_3D(self, path: str = None):
        if not path:
            path = self.path
        plot3 = plot_IR_3D.PlotIR(path=path)
        plot3.run()

    def plot_null(self, path: str = None):
        if not path:
            path = self.path
        plot_null = plot_nullify.PlotTIs(path=path)
        plot_null.run()

    def export_summary(self, path: str = None):
        if not path:
            path = self.path
        export_job = export_excels.CreateExcels(path=path)
        export_job.export_info()

    def move_files(self, file_name):
        rem_dir = r"{0}/derivatives/tsplots".format(self.path)
        new_dir = os.path.abspath(
            r"C:/Users/Owner/Desktop/cortical_layer_results/{0}".format(file_name)
        )
        shutil.move(rem_dir, new_dir)
        files = glob.glob(r"{0}\derivatives\feats\*\*\*ROI*".format(self.path))
        for f in files:
            os.remove(f)

    def run(self):
        self.create_rois(path=self.path)
        self.featquery(path=self.path)
        self.ts_gather(path=self.path)
        self.calc_ts_features(path=self.path)
        self.export_summary(path=self.path)
        self.plot_3D(path=self.path)
        self.plot_null(path=self.path)
        self.move_files(file_name=self.name)

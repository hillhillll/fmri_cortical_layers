function get_sorted_nii(src)
% converting dicom to nii
% must be seperated to dicom and nii folders:
mkdir([src,'/nii/Data_analysis'])
d = dir(src);
for i = 1:length(d)
    if d(i).isdir
        mkdir([src,'/nii/Data_analysis/',d(i).name]);
        dicm2nii([src,'/',d(i).name],[src,'/nii/Data_analysis/',d(i).name,'nii'])
    end
end

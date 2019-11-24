cur_dir = '/Users/glhrsqwbyz/Desktop/Projects/fMRI_Cortical_Layers/Pilot/YA_lab_Omri_Subj000120_20190410_1601/nii_SPM/2019-04-10_16-01/func'; %Enter func data dir
dir_arr = dir(cur_dir);
nii_subs = {};
j = 0;
all_niftis = struct('Name_of_scan',[],'Nifti_img',[],'Nifti_info',[]);
%%
for i = 1:length(dir_arr)
    subdir = dir_arr(i).name;
    if subdir(1)~= '.'
        j=j+1;
        n = 0;
        l=0;
        nii_subs{j} = subdir;
        all_niftis(j).Name_of_scan = nii_subs{j};
        new_dir = [cur_dir,'/',nii_subs{j},'/wrf'];
        this_folder = dir(new_dir);
        good_niftis = {};
        %%
        for k = 1:length(this_folder)
            if this_folder(k).name(1)~= '.'
                if this_folder(k).name(1:2) == 'wr'
                    l=l+1;
                    good_niftis{l} = this_folder(k).name;
                end
            end
        end
        all_niftis(j).Nifti_img = zeros([79 95 79 l]);
        for ind = 1:l
            this_nifti = good_niftis{ind};
            all_niftis(j).Nifti_info = niftiinfo([cur_dir,'/',nii_subs{j},'/wrf','/',this_nifti]);
            all_niftis(j).Nifti_img(:,:,:,ind) = niftiread([cur_dir,'/',nii_subs{j},'/wrf','/',this_nifti]);
        end
    end
end

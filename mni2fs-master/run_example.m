clear all
close all
clc

% Replace the following path with the path to the mni2fs toolbox folder
%%
toolboxpath = fileparts(which('mni2fs'));


%% Simple Auto Wrapper - All Settings are at Default and Scaling is Automatic
% Default threshold
close all
mni2fs_auto('AudMean.nii','rh')


%% Plot both hemispheres
% 99th Percentile threshold
close all
mni2fs_auto(fullfile(toolboxpath, 'examples/AudMean.nii'),'lh',0.99)
mni2fs_auto(fullfile(toolboxpath, 'examples/AudMean.nii'),'rh',0.99)
view([40 30])


%% Plot ROI and Overlay
close all
figure('Color','k','position',[20 72 800 600])

% Load and Render the FreeSurfer surface
S = [];
S.hem = 'rh'; % choose the hemesphere 'lh' or 'rh'
S.inflationstep = 6; % 1 no inflation, 6 fully inflated
S.plotsurf = 'inflated';
S.lookupsurf = 'smoothwm';
S.decimation = false; % Decimate the surface for speed. (Use FALSE for publishable quality figures).
S = mni2fs_brain(S);

% Plot an ROI, and make it semi transparent
S.mnivol = fullfile(toolboxpath, 'examples/AudMean.nii');
S.roicolorspec = 'm'; % color. Can also be a three-element vector
S.roialpha = 1; % transparency 0-1
S = mni2fs_roi(S); 
%%
% Add overlay, theshold to 98th percentile
NIFTI = 'HOA_heschlsL.nii'; % mnivol can be a NIFTI structure
S.mnivol = NIFTI;
S.clims_perc = 0.99; % overlay masking below 98th percentile
S.clims = [0 1];
S.climstype = 'pos';
S = mni2fs_overlay(S);
view([-122 8]) % change camera angle
mni2fs_lights % Dont forget to turn on the lights!
% Optional - lighting can be altered after rendering


%% For high quality output 
% Try export_fig package included in this release
% When using export fig use the bitmap option 
export_fig('filename.bmp','-bmp')


%% OR TRY MYAA for improved anti-aliasing without saving
myaa


%%
S = [];
S.hem = 'lh'; % choose the hemesphere 'lh' or 'rh'
S.inflationstep = 1; % 1 no inflation, 6 fully inflated
S.plotsurf = 'inflated';
S.lookupsurf = 'smoothwm';
S.decimation = true; % Decimate the surface for speed. (Use FALSE for publishable quality figures).
S.surfacealpha = 0.3;
S.surfacecolorspec = [0.8 0.8 0.8];
S = mni2fs_brain(S);
mni2fs_makeiso(fullfile(toolboxpath, 'examples/AudMean.nii'), 1, [1 0.5 0.3], 3, 1, 0)
mni2fs_lights
view([90 0])


function [IRdata,TIlist,minIRnii,AllIRnii,MPRAGEnii,series_index] = makeIRdata(folder, varargin)
%Folder of .dcm scans!
current_folder = pwd;
% building a 4 dimensional matrix dim(1+2) = image data, dim3 = image cut index in folder, dim4 = folder number
IREPI_flag = {'*IR-EPI*', '*_IR_*','*IREPI*'};

%% Read varargin
cfg = struct();
for ind=1:2:length(varargin)
    switch lower(varargin{ind})
        case 'subset'
            cfg.subset = varargin{ind+1};
            if ~islogical(cfg.subset)
                error('Subset configuration must be logical!');
            end
            %             case 'skullstripped'
            %                 cfg.brain_template = varargin{ind+1};
            %             otherwise
            %                 error(['The parameter ' varargin{ind+1} ' is not recognized.']);
    end
end

if ~isfield(cfg, 'subset')
    cfg.subset = false;
    subset_list = [];
end
%     if isfield(cfg, 'brain_template')
%         cfg.skull_stripped = true;
%     else
%         cfg.skull_stripped = false;
%     end


%% List IR-EPI dcm directories in path

cd(folder);
scan_dirs = [dir(IREPI_flag{1}), dir(IREPI_flag{2}), dir(IREPI_flag{3})];
if isempty(scan_dirs)
    error('pwd: %s\nCould not find any matching scan directories in current working directory!\n Please change working directory and try again.', pwd);
end
dirFlags = [];
for i = 1:length(scan_dirs)
    if scan_dirs(i).isdir && ~contains(scan_dirs(i).name,'Motor') && ~contains(scan_dirs(i).name,'Sensory') && ~contains(scan_dirs(i).name,'Sensor')
        dirFlags(i) = true;
    else
        dirFlags(i) = false;
    end
end
dirFlags = logical(dirFlags);
% Extract only those that are directories.
scan_dirs = scan_dirs(dirFlags);

%% Get IR data from each IR-EPI scan

% Create waitbar


% preset some paramaters for for loop
TIlist = [];
excluded_TIs = [];
k = 0;
series_index = struct();
prev_n_slices = 0;

% Loop through IR-EPI scan directories
for i = 1:length(scan_dirs)
    
    cd(scan_dirs(i).name);
    
    % List dcms within scan directory
    files = dir('*.dcm');
    if isempty(files)
        continue;
    end
    k_updated = 0; % keep track of TI dim index
    
    if length(files) ~= prev_n_slices && i ~= 1
        warning('Incoherent z dimension! Used to be %d and now %d!', prev_n_slices, length(files));
        IRdata(:, :, prev_n_slices, :) = [];
    end
    
    % get IR data from each dcm
    for j = 1:length(files)
        
        info=dicominfo(files(j).name);                   % read current dcm
        
        % break if TI already sampled
        if ~any(TIlist == info.InversionTime)
            series_index.(['TI' char(string(info.InversionTime))]) = info.SeriesNumber;
        elseif series_index.(['TI' char(string(info.InversionTime))]) ~= info.SeriesNumber
            sprintf('Series %d was found to be a repeat of TI%d and therefore omitted', info.SeriesNumber, info.InversionTime);
            break
        end
        
        
        % advance in fourth dimension
        if k_updated == 0
            TIlist = [TIlist, info.InversionTime];
            k = k+1;
            k_updated = 1;
        end
        % read data
        IRdata(:,:,j,k)=dicomread(files(j).name);    % read the data image of files(j) in foldername(i) to the 1st and 2nd dim of IRdata
        
        
    end
    
    prev_n_slices = length(files);
    
    
    
    
    cd ..
    
end

IRdata = imrotate(IRdata,-90);
[TIlist,sortInd] = sort(TIlist);
IRdata = IRdata(:,:,:,sortInd);
series_index = orderfields(series_index,sortInd);

%% Motion correction
%     [IRdata, ~] = Opt_affine(IRdata);
[optimizer, metric] = imregconfig('multimodal');
optimizer.InitialRadius = 0.000009;
optimizer.Epsilon = 1.5e-4;
optimizer.GrowthFactor = 1.01;
optimizer.MaximumIterations = 300;
fixed  = IRdata(:,:,:,8);
for i=2:size(subset_list)
    moving = IRdata(:,:,:,i);
    IRdata(:,:,:,i) = imregister(moving, fixed, 'affine', optimizer, metric);
end


%%
minTI = TIlist(find(TIlist>400,1,'first'));
minTIfolderPrefix = num2str(series_index.(['TI' num2str(minTI)]));
minTIfolder = dir(fullfile(folder,[minTIfolderPrefix '_*']));
dicm2nii(fullfile(folder,minTIfolder(1).name),folder,'nii');
delete(fullfile(folder,'dcmHeaders.mat'))
niipath = dir(fullfile(folder,'*.nii'));
minIRnii = load_untouch_nii(fullfile(folder,niipath(1).name));
AllIRnii = minIRnii;
minIRnii.hdr.hist.descrip = [minIRnii.hdr.hist.descrip 'TI=' num2str(minTI)];
AllIRnii.img = IRdata;
AllIRnii.hdr.dime.dim(1) = 4;
AllIRnii.hdr.dime.dim(5) = length(TIlist);
delete(fullfile(folder,niipath(1).name))

%%
MPRAGEfolder = dir(fullfile(folder,'*MPRAGE*'));
dicm2nii(fullfile(folder,MPRAGEfolder(1).name),folder,'nii');
delete(fullfile(folder,'dcmHeaders.mat'))
niipath = dir(fullfile(folder,'*.nii'));
MPRAGEnii = load_untouch_nii(fullfile(folder,niipath(1).name));
delete(fullfile(folder,niipath(1).name))

cd(current_folder)
end

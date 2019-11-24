function IRdata = CreateIRdata(folderName,fileName,TInum,varargin)
%Creating the Inversion Recovry data from a .nii file.
%folderName contains the directory in which the .nii files are
%located
%fileName contains the name of the .nii files, not including the
%number indicating the place in the series of TI used.
%TInum is a vector of integers, indicating the number of each slice being
%added to the IR data.
%In case the size of all the images contained in the .nii files is known,
%varargin{1} contains a vector indicating this size. for example:
%[68,68,14]
%Syntax:
%IRdata = CreateIRdata(folderName,fileFormat,TInum)
%[Pmap,M0map] = CreatePmap(IRdata,TIlist,k,imageSize)
if length(varargin) == 1
    imageSize = varargin{1};
    IRdata = zeros(imageSize(1),imageSize(2),imageSize(3));
elseif length(varargin) == 3
    imageSize = varargin{1};
    IRdata = zeros(imageSize(1),imageSize(2),imageSize(3));
    fileFormat = varargin{2};
    niiFolder = varargin{3};
    if fileFormat == '.dicm'
        dicm2nii(folderName,niiFolder);
        folderName = niiFolder;
    end
end

cd(folderName)
for i = 1:length(TInum)
    if TInum(i) > 99
        error('Number of different TIs must be under 99')
    end
    if TInum(i)<10
        thisFile = [fileName,'00',num2str(TInum(i)),'.nii'];
    else
        thisFile = [fileName,'0',num2str(TInum(i)),'.nii'];
    end
    Slice = niftiread(thisFile);
    IRdata(:,:,:,i) = Slice;
end


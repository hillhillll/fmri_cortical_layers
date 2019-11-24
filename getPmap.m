%This script will regularize the analysis of a probability map of Cortical
%layers based on MR T1 scans
uiwait(msgbox('Please choose the folder in which the .nii files are located in','Choose folder','modal'));
folderName = uigetdir;
filesFormat = string(input('Please enter the format of the scans (.dicm / .nii): '));
TIstart = input('Please enter the first slice`s number: ');
TIend = input('Please enter the last slice`s number: ');
TInum = [TIstart:TIend];
fileName = string(input('Please enter the name of all files, not including the slice number: '));
if filesFormat == '.nii'
    IRdata = CreateIRdata(folderName,fileName,TInum);
elseif filesFormat == '.dicm'
    uiwait(msgbox('Please choose the folder into which the converted .nii files will be extracted to','Choose nii folder','modal'));
    niiFolder = uigetdir;
    IRdata = CreateIRdata(folderName,fileName,TInum,'.dicm',niiFolder);
end

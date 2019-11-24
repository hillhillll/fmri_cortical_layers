function Coronal = makeCoronal(originalMRI, varargin)
if isempty(varargin)
    thisSlice = size(originalMRI,2)/2;
else
    thisSlice = varargin{1};
end
a = size(originalMRI,1);
b = size(originalMRI,3);
c = size(originalMRI,4);
T0 = maketform('affine',[0 -1; 1 0; 0 0]);
R2 = makeresampler({'cubic','nearest'},'fill');
for i = 1:c
    M1 = originalMRI(:,thisSlice,:,i);
    M2 = reshape(M1,[a b]);
    Coronal(:,:,i) = imtransform(M2,T0,R2);
end
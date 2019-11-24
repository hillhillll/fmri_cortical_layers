function showPmap(Pmap,IRdata,k,GM)
figure()
m = 3;
n = 5;
subplot(m,n,1)
if ndims(Pmap)<4
    imagesc(IRdata(:,:,size(IRdata,3)/2))
    title('Original coronal slice')
    Pmap = sort(Pmap,3);
else
%     imagesc(IRdata(:,:,size(IRdata,3)/2,size(IRdata,4)/2))
%     title('Original horizontal slice')
    [sortedMu,sortInd] = sort(GM.mu);
    Pmap = Pmap(:,:,:,sortInd);
end
mus = sort(GM.mu);
for i = 1:k
    thisT = num2str(mus(i));
    subplot(m,n,i+1)
    if ndims(Pmap)<4
        imagesc(Pmap(:,:,i))
    else
        imagesc(Pmap(:,:,size(Pmap,3)/2,i))
    end
    title(thisT)
end
end

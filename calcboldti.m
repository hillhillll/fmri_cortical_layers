function [err]=calcboldti(x, data,  TIlist, BOLD, varargin)
%function [err]=calcboldti(x, data,  TIlist, BOLD)
if ~isempty(varargin)
    T1vec = varargin{1};
    A=x(1:end-1);
else
    A = x(1:(end-1)/2);
    T1vec = x((end-1)/2:end-1);
end
nlayers = length(A);
nTI=length(TIlist);
S0=x(end);
%T1vec(1:5)=x(6:10);
for j=1:nTI
    for i=1:nlayers
        newdata(:,j,i)= S0*(1-2*exp(-TIlist(j)/T1vec(i))).*A(i).*BOLD;
    end
end
newdata=sum(newdata,3)';
newdata = abs(newdata);
for i = 1:size(newdata,1)
    newdata(i,:) = newdata(i,:)./sum(newdata(i,:));
end
err=newdata-data;
err=err(:);
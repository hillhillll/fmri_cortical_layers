function [varargout] = plotGMModel4Gal(T1Histogram,GMModel,varargin)
%Plot T1 histogram data with overlaying gaussian mixture model
%distributions
%
%   This function displays the T1 histogram data as a pdf histogram, and
%   overlays it with the mixture distributions composing it.
%
%
% Syntax:
%   plotGMM(T1Histogram,GMModel)
%   plotGMM(T1Histogram,GMModel,Name,Value)
%
%
% Description:
%   plotGMM(T1Histogram,GMModel) plots the T1 histogram T1Histogram and
%   overlays it with the GMModelribution object GMModel
%
%   plotGMM(T1Histogram,GMModel,Name,Value) also displays further
%   information, such as legend or notations
%
% Input arguments:
%
%   T1Histogram - a 1xn vector of the T1 histogram values
%   GMModel - a GMModel object calculated from T1Histogram
%   Name-Value pairings:
%          displayLegend - a logical that determines whether to display a
%                          legend of the mixture distribution means.
%                          Default: *false*.
%          displayMu - to be used in future versions. Default: *false*.
%          displaySigma - to be used in future versions. Default: *false*.
%          displayPhi - to be used in future versions. Default: *false*.
%          saveFig - to be used in future versions. Default: *false*.
%          saveName - to be used in future versions. Default: 'GMM_Histogram'.
%          saveFormat - to be used in future versions. Default: 'png'.
%
% Output arguments:
%   To be used in future versions
figure()
displayLegend = true;
displayMu = false; % to be used in future version
displaySigma = false; % to be used in future version
displayPhi = false; % to be used in future version
saveFig = false;
saveName = 'GMM_Histogram';
saveFormat = 'png';
if rem(length(varargin),2) ~= 0
    error('Incorrect number of input arguments. Name-Value must be in pairs.')
end
for ind=1:2:length(varargin)
    switch(lower(varargin{ind}))
        case 'displaylegend'
            displayLegend = varargin{ind+1};
        case 'displaymu'
            displayMu = varargin{ind+1};
        case 'displaysigma'
            displaySigma = varargin{ind+1};
        case 'displayphi'
            displayPhi = varargin{ind+1};
        case 'savefig'
            saveFig = varargin{ind+1};
        case 'savename'
            saveName = varargin{ind+1};
        case 'saveformat'
            saveFormat = varargin{ind+1};
        otherwise
            error('Unrecognized Name-Value pairing')
    end
end
h = histogram(T1Histogram,400,'Normalization','pdf','EdgeColor','none','FaceColor',[0 0 0],'FaceAlpha',0.8);
k = GMModel.NumComponents;
mu = GMModel.mu;
sigma = sqrt(squeeze(GMModel.Sigma));
phi = GMModel.ComponentProportion';
[mu,I] = sort(mu);
sigma = sigma(I);
phi = phi(I);
hold on
plot(0:3999,pdf(GMModel,[0:3999]'),'k','LineWidth',2);
ColorScheme = hsv(k);
% ColorScheme = ColorScheme(1:k,:);
for j=1:k
    x(j,1:500) = linspace(mu(j)-4*sigma(j),mu(j)+4*sigma(j),500);
    y(j,1:500) = phi(j)*normpdf(x(j,1:500),mu(j),sigma(j));
end
set(gca,'ColorOrder',ColorScheme)
%pl = plot(x(1:13,:)',y(1:13,:)','LineWidth',2);
pl = plot(x',y','LineWidth',2);
hold off

xlim([0 2700])
ylim([0 1.5*10^-3])
set(gca,'FontSize',30,'TickLength',[0 0])
if displayLegend
    lgd_txt = strcat('\mu =',{' '}, num2str(mu),{' '},'ms');
    legend(pl,lgd_txt,'FontSize',20)
    xlabel('T1 [ms]','FontSize',35);
    ylabel('PDF','FontSize',35)
end

switch nargout
    case 0
    case 1
        varargout{1} = h;
    case 2
        varargout{1} = h;
        varargout{2} = pl;
end

end

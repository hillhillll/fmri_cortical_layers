function TMModel = fitPriorTMModels(T1Histogram,n_components,gm_range,varargin)
% uses default parameters for now, will be expanded in the future
if nargin<3
    gm_range = [800 1800];
end
if nargin<2
    n_components = [2 6 2];
end
T1Histogram = reshape(T1Histogram,[],1); 
fitKernel = true;
Start = 'kmeans';
for ind=1:2:length(varargin)
    switch(lower(varargin{ind}))
        case 'k'
            K = varargin{ind+1};
        case 'fitkernel'
            fitKernel = varargin{ind+1};
        case 'start'
            St
            
            
            
            rt = varargin{ind+1};
        otherwise
            error(['The parameter ' varargin{ind+1} ' is not recognized by fitTMModel.']);
            
    end
end
wm_pv = sum(T1Histogram<gm_range(1))/length(T1Histogram);
gm_pv = sum(T1Histogram>gm_range(1) & T1Histogram<gm_range(2))/length(T1Histogram);
csf_pv = sum(T1Histogram>gm_range(2))/length(T1Histogram);

WM_model = fittmdist(T1Histogram(T1Histogram<gm_range(1)),n_components(1),'fitkernel',fitKernel,'Start','kmeans');
GM_model = fittmdist(T1Histogram(T1Histogram>gm_range(1) & T1Histogram<gm_range(2)),n_components(2),'fitkernel',fitKernel,'Start','kmeans');
CSF_model = fittmdist(T1Histogram(T1Histogram>gm_range(2)),n_components(3),'fitkernel',fitKernel,'Start','kmeans');

mu = [WM_model.mu ; GM_model.mu ; CSF_model.mu];
Sigma = [WM_model.Sigma ; GM_model.Sigma ; CSF_model.Sigma];
nu = [WM_model.nu ; GM_model.nu ; CSF_model.nu];
phi = [wm_pv* WM_model.phi ; gm_pv * GM_model.phi ; csf_pv * CSF_model.phi];
TMModel = tmdistribution(mu,Sigma,phi,nu);

end
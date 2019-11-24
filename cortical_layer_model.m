function [layerparams,RESNORM,RESIDUAL,EXITFLAG,OUTPUT] = cortical_layer_model(compN,action,guessT1,varargin)
layer_guess = rand(1,compN);
layer_guess = layer_guess./sum(layer_guess);
s0 = 5000+rand(1)*(10000-5000);
%x0=[0.2 0.2 0.2 0.4 500 530 570 630 710 5000]; %  Initial guess for A1-->3
if strcmp(action,'Motor')
    rel_table = readtable("C:\Users\Owner\Desktop\fsl_pipeline_trial\derivatives\tsplots\mean_ts\task-Motor_acq-IREPITI_summary.xlsx");
    full_BOLD = readtable("C:\Users\Owner\Desktop\fsl_pipeline_trial\derivatives\tsplots\mean_ts\task-Motor_acq-SE_summary.xlsx");
%     j=1;
%     for i = 1:10
%         BOLD(i) = mean(full_BOLD.acq_Gre(j)+full_BOLD.acq_Gre(j+1));
%         j=j+2;
%     end
elseif strcmp(action,'Sensory')
    rel_table = readtable("C:\Users\Owner\Desktop\fsl_pipeline_trial\derivatives\tsplots\mean_ts\task-Sensory_acq-IREPITI_summary.xlsx");
    full_BOLD = readtable("C:\Users\Owner\Desktop\fsl_pipeline_trial\derivatives\tsplots\mean_ts\task-Sensory_acq-SE_summary.xlsx");
%     j=1;
%     for i = 1:10
%         BOLD(i) = mean(full_BOLD.acq_Gre(j)+full_BOLD.acq_Gre(j+1));
%         j=j+2;
%     end
end
data = rel_table(:,2:end);
data = data.Variables';
BOLD = full_BOLD(:,2).Variables';
%x0=[0.2 0.2 0.2 0.4 1000]; %  Initial guess for A1-->3
TIlist=[630 650 670 690 710 730 750 930];
%min_val=[0 0 0 0 0 0 0 0 0 0 0 ];
h=optimset('DiffMaxChange',1e-1,'DiffMinChange',1e-3,'MaxIter',20000,...
    'MaxFunEvals',20000,'TolX',1e-6,...
    'TolFun',1e-6, 'Display', 'off');
if guessT1
    T1guess = sort(100+rand(1,compN)*(1000-100)); % Numerical guesses of the three T1s
    x0 = [layer_guess T1guess s0];
    min_val=[zeros(1,compN) repmat(100,1,compN), 5000];
    max_val=[ones(1,compN), repmat(1000,1,compN), 10000];
    [layerparams,RESNORM,RESIDUAL,EXITFLAG,OUTPUT]=lsqnonlin('calcboldti',...
        double(x0),min_val,max_val,h,data,  TIlist, BOLD); %T1vec, S0);
    partial_cont = layerparams(1:(end-1)/2);
    partial_cont = partial_cont./sum(partial_cont);
    layerparams = [partial_cont layerparams((end-1)/2+1:end)];
else
    T1vec=varargin{1}; % Numerical values of the three T1s
    x0 = [layer_guess s0];
    min_val=[zeros(1,compN), 5000];
    max_val=[ones(1,compN), 10000];
    [layerparams,RESNORM,RESIDUAL,EXITFLAG,OUTPUT]=lsqnonlin('calcboldti',...
        double(x0),min_val,max_val,h,data,  TIlist, BOLD ,T1vec); %S0);
    partial_cont = layerparams(1:end-1);
    partial_cont = partial_cont./sum(partial_cont);
    layerparams = [partial_cont T1vec layerparams(end)];
end
% BOLD % a vector of the 10 points bold response of GE EPI
% a list of the different TI used (by the order to data)
% S0 = % a number for the signal at TI=0;
%data =% a matrix of the data in format timexTI

end

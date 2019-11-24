function [layerparams_motor,layerparams_sensory] = plot_layerparams(to_save, subnum, varargin)

%figure('NumberTitle', 'off', 'Name', 'Model estimate - smoothed');
gm_range = [800 1800];
if subnum == 0
    if isempty(varargin)
        [layerparams_motor,RESNORM,RESIDUAL,EXITFLAG,OUTPUT] = cortical_layer_model_subject('Mean','Motor',0);
        [layerparams_sensory,RESNORM,RESIDUAL,EXITFLAG,OUTPUT] = cortical_layer_model_subject('Mean','Sensory',0);
    else
        [layerparams_motor,RESNORM,RESIDUAL,EXITFLAG,OUTPUT] = cortical_layer_model_subject('Mean','Motor',0,'Test');
        [layerparams_sensory,RESNORM,RESIDUAL,EXITFLAG,OUTPUT] = cortical_layer_model_subject('Mean','Sensory',0,'Test');
    end
else
    if isempty(varargin)
        [layerparams_motor,RESNORM,RESIDUAL,EXITFLAG,OUTPUT] = cortical_layer_model_subject(subnum,'Motor',0);
        [layerparams_sensory,RESNORM,RESIDUAL,EXITFLAG,OUTPUT] = cortical_layer_model_subject(subnum,'Sensory',0);
    else
        [layerparams_motor,RESNORM,RESIDUAL,EXITFLAG,OUTPUT] = cortical_layer_model_subject(subnum,'Motor',0,'Test');
        [layerparams_sensory,RESNORM,RESIDUAL,EXITFLAG,OUTPUT] = cortical_layer_model_subject(subnum,'Sensory',0,'Test');
    end
end
%smoothed_motor = smooth(layerparams_motor(1:10));
smoothed_motor = smooth(layerparams_motor(3:8));
smoothed_motor = smoothed_motor./sum(smoothed_motor);
%smoothed_sensory = smooth(layerparams_sensory(1:10));
smoothed_sensory = smooth(layerparams_sensory(3:8));
smoothed_sensory = smoothed_sensory./sum(smoothed_sensory);
%[x,i] = sort(layerparams_motor(10+1:10*2));
[x,i] = sort(layerparams_motor(10+3:10*2-2));
figure('NumberTitle', 'off', 'Name', 'Model estimate - smoothed');
bar(x',[smoothed_motor(i),smoothed_sensory(i)],'BarWidth',2)
title('smoothed motor and sensory estimates accroding to cortical-layers fMRI model')
xlabel('T1 value')
ylabel('Partial contribution to signal')
grid on
%xlim([min(layerparams_motor(10+1:10*2)-200) max(layerparams_motor(10+1:10*2)+200)])
xlim([min(layerparams_motor(10+3:10*2-2)-200) max(layerparams_motor(10+3:10*2-2)+200)])
hold on
drawbrace([gm_range(1),max(smoothed_motor+0.02)],[gm_range(2),max(smoothed_motor+0.02)],20)
legend('Motor','Sensory','GM range')
%scatter(layerparams_sensory(4:6),layerparams_sensory(1:3))
%bar(layerparams_sensory(Ncomp+1:Ncomp*2),data_to_plot)
if to_save
    if isempty(varargin)
        saveas(gcf,'C:\Users\Owner\Desktop\cortical_layer_results\model_estimate_smoothed.png')
    else
        saveas(gcf,'C:\Users\Owner\Desktop\cortical_layer_results\model_check_estimate_smoothed.png')
    end
end
hold off
figure('NumberTitle', 'off', 'Name', 'Model estimate - raw');
bar(layerparams_motor(10+1:10*2),[layerparams_motor(1:10)',layerparams_sensory(1:10)'],'BarWidth',2)

hold on
drawbrace([gm_range(1),max(layerparams_motor(1:10)'+0.02)],[gm_range(2),max(layerparams_motor(1:10)'+0.02)],20)
title('Raw motor and sensory estimates accroding to cortical-layers fMRI model')
xlabel('T1 value')
ylabel('Partial contribution to signal')
grid on
%xlim([min(layerparams_motor(10+1:10*2)-200) max(layerparams_motor(10+1:10*2)+200)])
xlim([min(layerparams_motor(10+3:10*2-2)-200) max(layerparams_motor(10+3:10*2-2)+200)])
hold on
%plot(layerparams_sensory(Ncomp+1:Ncomp*2),layerparams_sensory(1:Ncomp),'g-o','LineWidth',2)
legend('Motor','Sensory','GM range')
hold off
if to_save
    if isempty(varargin)
        saveas(gcf,'C:\Users\Owner\Desktop\cortical_layer_results\model_estimate_raw.png')
    else
        saveas(gcf,'C:\Users\Owner\Desktop\cortical_layer_results\model_check_estimate_raw.png')
    end
end

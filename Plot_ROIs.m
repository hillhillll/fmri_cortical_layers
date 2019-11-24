function Plot_ROIs(Motor_ROIs,Sensory_ROIs)
is_norm = input('normalize Y axis?');
figure()
j=1;
k=1;
%Plot Gre scans
subplot(5,2,1)
plot(Motor_ROIs(1).Time_Course)
title(Motor_ROIs(j).Scan)

subplot(5,2,2)
plot(Sensory_ROIs(1).Time_Course)
title(Sensory_ROIs(k).Scan)

%Plot IR SE scans
for i = 3:10
    subplot(5,2,i)
    if mod(i,2) == 1
        j = j+1;
        plot(Motor_ROIs(j).Time_Course)
        title(Motor_ROIs(j).Scan)
        if is_norm %normalize Y axis if needed
            ylim([0 1])
        end
    else
        k = k+1;
        plot(Sensory_ROIs(k).Time_Course)
        title(Sensory_ROIs(k).Scan)
        if is_norm %normalize Y axis if needed
            ylim([0 1])
        end
    end
end
end

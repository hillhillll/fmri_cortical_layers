function [minBIC,numOfComponents,GMModels] = BestModel(Data,from,to)
BIC = zeros(1,to);
GMModels = cell(1,to);
for k = from:to
    fprintf('%dth comp\n',k)
    GMModels{k} = fitgmdist(Data,k);
    BIC(k) = GMModels{k}.BIC;
    %     if k >= 3
    %         if GMModels{k}.BIC>GMModels{k-1}.BIC && GMModels{k}.BIC>GMModels{k-2}.BIC
    %             break
    %         end
    %     end
end
[minBIC,numOfComponents] = min(BIC);
numOfComponents


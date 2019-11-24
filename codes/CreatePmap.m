function [Pmap,M0map] = CreatePmap(IRdata,TIlist,k,varargin)
%Create a probability map based on an Inversion Recovery scan (IRdata), with a list
%of TIs (TIlist), num of components t be used while generating the Gaussian
%Mixture model (k) and a logical value indicating whether to present the
%probability map or not.
%Syntax: 
%[Pmap,M0map] = CreatePmap(IRdata,TIlist,k)
%[Pmap,M0map] = CreatePmap(IRdata,TIlist,k,showPmap)
if length(varargin) == 1
    dispPmap = varargin{1};
end
[T1map,M0map,normM0map] = calcT1map(IRdata,TIlist);
%Calculate a whole-brain map of T1-values in sub-voxel resolution
%
%   This function calculates the T1-values for a whole-brain inversion
%   recovery (IR) data set. The function is given a data set, a list of the
%   inversion times (TI) and the maximum number of components per voxel,
%   and outputs a 4-dimensional T1map (three dimensions are spatial, the
%   fourth dimension is the sub-voxel dimension), a matching map of M0
%   values, and also a map of those M0 values normalized per voxel.
T1Histogram = genT1Histogram(T1map,normM0map);
%Generate a whole-brain histogram of T1-values proportional to their
%partial volume
%
%   This function generates a whole-brain histogram of the T1-values that
%   is proportional to their partial volume, represented by each
%   T1-component's M0 value normalized per-voxel.
GM = fitgmdist(T1Histogram,k);
%FITGMDIST Fit a Gaussian mixture distribution to data.
%   GM = FITGMDIST(X,K) fits a Gaussian mixture distribution with K
%   components to the data in X.  X is an N-by-D matrix.  Rows of X
%   correspond to observations; columns correspond to variables. FITGMDIST
%   fits the model by maximum likelihood, using the
%   Expectation-Maximization (EM) algorithm.
Pmap = calcPmapGM(T1map,normM0map,GM);
Generate a volume probability map for multiple component distributions
%extracted from whole-brain T1-values
%
%   This function calculates the volume probability in each voxel for
%   multiple component distributions of different brain tissue. These
%   distributions are extractedby fitting a Gaussian mixture model to the
%   whole-brain histogram of T1-values with the function fitGMModel.
if dispPmap == True
    showPmap(Pmap,IRdata,k,GM)
end

    


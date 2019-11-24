figure('units','normalized','outerposition',[0 0.05 0.9 0.95]);%'Visible','off'

axis equal
set(gca,'Position',[-0.13 -0.13 1.27 1.27])
[pt,vt,ct]=isosurface(surface,zeros(size(surface)));
patch('Vertices', vt, 'Faces', pt, ...
    'FaceVertexCData', ct, ...
    'FaceColor',[0.8 0.8 0.8], ...
    'edgecolor', 'none',...
    'FaceAlpha',1);

axis vis3d;
%axis equal;
axis off;
%view([0 0]);

[pt,vt,ct]=isosurface(surface,values .* values./values);
%         at = ones(size(ct));
%         at(isnan(ct)) = 0;

patch('Vertices', vt, 'Faces', pt, ...
    'FaceVertexCData', ct, ...
    'FaceColor','Flat', ...
    'edgecolor', 'none',...
    'FaceAlpha',1);
axis vis3d;
%    axis equal;
axis off;
view([0  0])
%camlight; lighting phong
camlight; lighting gouraud
%         cmap = flipud(hot);
%         cmap = cmap(2:end-10,:);
%         colormap(cmap)
cmap = jet;
cmap = cmap(3:end-2,:);
colormap(cmap)

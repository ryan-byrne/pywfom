% [m,data] = LoadData(Path,m) loads a specified WFOM dataset.
%
% Version 1.7
%
% Inputs:
%
% Path - full path to stim run files (REQUIRED)
%
% NEW for v1.6: all options must be passed into the m structure. Use
% m = makem to create a default m structure, then alter your parameters as
% neccesary before running LoadData().
%
% m.outputs - string with these characters: rgblodn12R.
% Red, Green, Blue, Lime, hbO, hbR, Neural. 1 and 2 are for webcams 1 and 2.
% R is for rotary. Order doesn't matter.
% Default is 'odn'.
%
% m.dsf - downsample factor (Integer).
% Default is 1.
%
% m.dpf - array of two pathlengths for GCaMP correction (or for jRGECO
% correction)
% Default is [.5 .6].
%
% m.baseline - passed as a vector containing what frames
% you want to use as a baseline for correction.
% Default is [30:100].
%
% m.loadpct - 0-1. This loads a ratio of the frames from the beginning of
% the run, where 1 is the whole run or .5 is half of it.
% Default is 1.
%
% m.PCAcomps - 0 if you don't want to perform PCA, and n if you want it
% reconstructed with components 1:n.
%
% Other optional arguments (placed into m struct):
% m.noload = 1          : load the metadata only
% m.corr_flicker = 1    : perform flicker correction
% m.gettruestim = 1     : read the stimCCD bin files and get the real stim values
% m.do_PCA = 1          : perform PCA noise reduction on the data before conversion
% m.bkgsub (zyla) = 1   : performs background subtraction using first 3
%                         frames from blank recording
% Outputs:
% m: metadata struct
% data: data struct that includes WFOM and webcam image matrices.

function [m,data] = LoadData(varargin)
% VERSION HISTORY
%
% 5-11-18 - added crop to zyla loading so that outputs are square.
% v1.0    - added flicker correction.

% 5-31-18 - removed large number of inputs and made most of them optional.
% v1.1    - added webcam load functionality.
%         - added stim file reading for accurate stimulus information.

% 6-1-18  - added functionality to load a percentage of the dataset.
% v1.3

% 6-8-18  - added real time of stim writing for first and last files in
% v1.4      directory

% 8-9-18  - added flicker correction for all channels.
% v1.5    - added PCA via the 'do_PCA' flag

% 10-9-18 - added rotation
% v1.6    - updated input parsing to move all options to be placed into m
%           structure.
%         - added JRGECO1a analysis, as well as lime channel support
%         - added the ability to specify how many PCA components you want
%         - added new webcam .avi load functionality
%         - added rotary load code

% 5-29-19 - added some error dlgs, ported v17 to the current version.
% v1.7    - added cropping for BW file
%         - renamed the output 'rcamp' to 'jrgeco'
%         - fixed the textprogressbar bug
%         - (12/2/19) fixed a bug where some m fields were overwritten if m
%           was not a varargin
%         - (12/2/19) added support for acute mouse
%
% TO DO
%         - add 'spool index' loading for random stim datasets
%         - add blank frame deletion from zyla data
%         - add stim averaging functionality
%         - FLIR camera support(?)

disp('LoadData version 1.7')
addpath(genpath('/local_mount/space/juno/1/Software/MIAO/'))
warning('off','all')

h.m.fulldir = varargin{1};
try
    % Chronic mouse
    h.m.mouse = regexp(h.m.fulldir,'[cm]+[0-9]+(_)[0-9]+','Match');
    if isempty(h.m.mouse)
        % Acute mouse
        h.m.mouse = regexp(h.m.fulldir,'[m]+[0-9]+','Match');
    end
    h.m.mouse = h.m.mouse{:};
catch
    errordlg('ERROR: mouse number not determined. Please send in mouse number via the m structure')
end
h.m.run = regexp(h.m.fulldir,'(run)[A-Z]*[0-9]?','Match');
if ~isempty(h.m.run)
    h.m.run = h.m.run{1};
    h.m.stim = str2double(regexp(regexprep(h.m.fulldir,'/',''),'[0-9]+$','Match'));
    h.m.CCDdir = regexprep(varargin{1},[h.m.run '.*'],'');
end

% This folds in the fieldnames of the imported m struct into
% the already existing h.m struct. Imported m struct overrides
% duplicate fields.
if numel(varargin) == 2
    f = fieldnames(varargin{2});
    for j = 1:length(f)
        h.m.(f{j}) = varargin{2}.(f{j});
    end
else
    h.m = makem(h.m);
    disp('No m found. using default m...')
end
% Determine missing fields and substitute defaults
if isfield(h.m,'CCDdir')
    h = GetMetaData(h);
end
if h.m.noload
    data = 'No data loaded'; m = h.m;
    disp('Done')
    return
end

%%%%%%%%%%%%%%%%%%%%%%%%%%% IXON LOAD CODE %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
if strcmp(h.m.camera,'ixon') && ~isempty(regexp(h.m.outputs,'[rgbodnP]'))
    textprogressbar(sprintf(['Loading ' h.m.mouse ' ' h.m.run ' stim ' mat2str(h.m.stim) '\n']))
    newdim = [h.m.height/h.m.dsf h.m.width/h.m.dsf];
    for i = 1:h.m.nLEDs
        data.(h.m.LEDs{i}) = zeros(newdim(1), newdim(2), round(h.m.nFrames*(h.m.loadpct(2)-h.m.loadpct(1))/h.m.nLEDs));
    end

    % Get stim folder names
    tmp = dir(fullfile(h.m.CCDdir, h.m.run));
    tmp(~[tmp.isdir]) = []; tmp(cellfun('prodofsize', {tmp.name}) < 3) = [];
    stimfolders = {tmp.name}; clear tmp; blankflag = 0;
    tmp = dir(fullfile(h.m.CCDdir, h.m.run,stimfolders{1}));
    tmp(cellfun('isempty', regexpi({tmp.name}, '\.dat$'))) = []; datfiles = {tmp.name};
    for i = 1:length(datfiles)
        fid = fopen(fullfile(h.m.CCDdir, h.m.run,stimfolders{1},datfiles{i}),'r','l');
        tmp = fread(fid,[h.m.height h.m.width],'uint16','l');
        data.blanks(:,:,i) = mean(mean(reshape(tmp,[h.m.dsf,newdim(1),h.m.dsf,newdim(2)]),3),1);
        fclose(fid);
    end
    databg = squeeze(nanmean(data.blanks,3));
    %if h.m.bkgsub == 0
        databg = databg*0;
    %end
    if h.m.loadpct(1) == 0
        h.m.loadpct(1) = 1/h.m.nFrames;
    end
    h.m.framestoload = round(h.m.nFrames*h.m.loadpct(1):h.m.nLEDs:round(h.m.nFrames*h.m.loadpct(2)))-1;
    h.m.framestoload(end) = [];

    n = 0;
    for i = h.m.framestoload
        n = n + 1;
        for j = 1:h.m.nLEDs
            fid = fopen(fullfile(h.m.fulldir,  [h.m.run repmat('0',[1,10-size(num2str(i+j-1),2)]) num2str(i+j-1) '.dat']),'r','l');
            tmp = fread(fid,[h.m.height h.m.width],'uint16','l');
            if h.m.dsf == 1
                data.(h.m.LEDs{j})(:,:,n) = tmp-databg;
            else
                data.(h.m.LEDs{j})(:,:,n) = squeeze(mean(mean(reshape(tmp,[h.m.dsf,newdim(1),h.m.dsf,newdim(2)]),3),1))-databg;
            end
            fclose(fid);
        end
        if mod(i,10)
            if h.m.isgui
                h.status.String = sprintf('\n\n %i %% complete',round(i*100/h.m.nFrames)); drawnow
            else
                try
                    textprogressbar(round(n*100/length(h.m.framestoload)));
                catch
                    textprogressbar(sprintf(['Loading ' h.m.mouse ' ' h.m.run ' stim ' mat2str(h.m.stim) '\n']))
                end
            end
        end
    end

    textprogressbar(' Done')

%%%%%%%%%%%%%%%%%%%%%%%%%%% ZYLA LOAD CODE %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

elseif strcmp(h.m.camera,'zyla') && ~isempty(regexp(h.m.outputs,'[rgbodnlP]'))
    zylaInfoFilePath = fullfile(h.m.fulldir,'acquisitionmetadata.ini');
    FID = fopen(zylaInfoFilePath, 'r');
    zylaMetaData = fread(FID, '*char')';
    fclose(FID);
    AOIHeight_start = strfind(zylaMetaData, 'AOIHeight = ');
    AOIWidth_start = strfind(zylaMetaData, 'AOIWidth = ');
    AOIStride_start = strfind(zylaMetaData, 'AOIStride = ');
    PixelEncoding_start = strfind(zylaMetaData, 'PixelEncoding = ');
    ImageSizeBytes_start = strfind(zylaMetaData, 'ImageSizeBytes = ');
    ImageSizeBytes_end = strfind(zylaMetaData, '[multiimage]')-1;
    ImagesPerFile_start = strfind(zylaMetaData, 'ImagesPerFile = ');
    ImageSize = str2double(zylaMetaData(ImageSizeBytes_start+length('ImageSizeBytes = '):...
        ImageSizeBytes_end));
    numDepths = str2double(zylaMetaData(AOIHeight_start+length('AOIHeight = '):...
        AOIWidth_start-1));
    strideWidth = str2double(zylaMetaData(AOIStride_start+length('AOIStride = '):...
        PixelEncoding_start-1));
    numLatPix = strideWidth/2;
    numFramesPerSpool = str2double(zylaMetaData(ImagesPerFile_start+ length('ImagesPerFile = ')...
        :end));

    numColumns = numDepths + h.m.offsetfactor;
    numRows = numLatPix;
    newdim = floor([numRows/h.m.dsf, numColumns/h.m.dsf]);
    for i = 1:length(dir(fullfile(h.m.fulldir,'*.dat'))) % removed -1 here: may need to undo!
        temp = i-1; % added -1 here. this avoids not loading the 0000000000spool.dat file
        for j = 1:10
            a(i,j) = mod(temp, 10^j)/(10^(j-1));
            temp = temp-mod(temp, 10^j);
        end
        tempName = mat2str(a(i,:));
        tempName = tempName(2:end-1);
        tempName = tempName(find(tempName ~= ' '));
        tempName = [tempName 'spool.dat'];
        namesOut{i} = tempName;
    end
    if h.m.loadpct(1) == 0
        h.m.loadpct(1) = 1/numel(namesOut);
    end
    h.m.spoolsLoaded = round(numel(namesOut)*h.m.loadpct(1):round(numel(namesOut)*h.m.loadpct(2)));
    filesToLoad = namesOut(h.m.spoolsLoaded);
    FID = fopen(fullfile(regexprep(h.m.fulldir,'[_][0-9]$',''),'0000000000spool.dat'));
    rawData = fread(FID, 'uint16=>uint16');
    fclose(FID);
    numFramesInThisSpool = floor(length(rawData)/(numRows*numColumns));
    numPixelsToReshape = numRows * numColumns * numFramesInThisSpool;
    try
        rawData = (reshape(rawData(1:numPixelsToReshape),[numRows,numColumns,numFramesPerSpool]));
    catch
        disp([sprintf('reshaping failed. Please check offset factor and adjust to proper value.\n Height = %i, Width = %i, factors = ',numRows,numColumns) mat2str(divisor(numel(rawData)/numRows))])
        return
    end
    % This switches height and width is nrot is odd
    if mod(h.m.nrot,2) == 1
        height = h.m.height;
        h.m.height = h.m.width;
        h.m.width = height;
    end
    for i = 1:h.m.nLEDs
        tmp = rawData(:,:,i);
        tmp = tmp(1:h.m.height,1:h.m.width,:);
        if h.m.bkgsub
            data.bkg.([h.m.LEDs{i}]) = tmp;
        else
            data.bkg.([h.m.LEDs{i}]) = tmp*0;
        end
    end
    try
        textprogressbar(sprintf(['Loading ' h.m.mouse ' ' h.m.run ' stim ' mat2str(h.m.stim) '\n']));
    catch
        textprogressbar('Loading...\n');
    end
    for i = 1:h.m.nLEDs  % preallocate
        data.(h.m.LEDs{i}) = (zeros(h.m.height/h.m.dsf,h.m.width/h.m.dsf,ceil(numFramesPerSpool.*length(filesToLoad)/h.m.nLEDs)));
    end

    for k = 1:h.m.nLEDs
        start = k;
        indexx.(h.m.LEDs{k}){1} = start:h.m.nLEDs:numFramesPerSpool;
        dsindex.(h.m.LEDs{k}){1} = 1:size(indexx.(h.m.LEDs{k}){1},2);
        indnum.(h.m.LEDs{k}){1} = length(dsindex.(h.m.LEDs{k}));
    end

    for i = 2:length(filesToLoad)
        for k = 1:h.m.nLEDs
            last = max(indexx.(h.m.LEDs{k}){i-1});
            skip = numFramesPerSpool-last;
            indexx.(h.m.LEDs{k}){i} = (h.m.nLEDs-skip-1)+[1:h.m.nLEDs:(numFramesPerSpool-(h.m.nLEDs-skip-1))]; % location in each batch of LEDs
            dsindex.(h.m.LEDs{k}){i} = max(dsindex.(h.m.LEDs{k}){i-1})+[1:size(indexx.(h.m.LEDs{k}){i},2)];
            indnum.(h.m.LEDs{k}){i} = length(dsindex.(h.m.LEDs{k}){i});
        end
    end

    for j = 1:length(filesToLoad)
        FID = fopen(fullfile(h.m.fulldir,filesToLoad{j}));
        rawData = fread(FID, 'uint16=>uint16');
        fclose(FID);
        numFramesInThisSpool = floor(length(rawData)/(numRows*numColumns));
        numPixelsToReshape = numRows * numColumns * numFramesInThisSpool;
        if j == 1
            try
                rawData=(reshape(rawData(1:numPixelsToReshape),[numRows,numColumns,numFramesPerSpool]));
            catch
                numColumns = numDepths + 1;
                numFramesInThisSpool = floor(length(rawData)/(numRows*numColumns));
                numPixelsToReshape = numRows * numColumns * numFramesInThisSpool;
                rawData=(reshape(rawData(1:numPixelsToReshape),[numRows,numColumns,numFramesPerSpool]));
            end
        else
            rawData=(reshape(rawData(1:numPixelsToReshape),[numRows,numColumns,numFramesPerSpool]));
        end
        % Crop rawdata to original resolution
        rawData = rawData(1:h.m.height,1:h.m.width,:);

        for k = 1:h.m.nLEDs
            if h.m.dsf > 1
                data.(h.m.LEDs{k})(:,:,dsindex.(h.m.LEDs{k}){j}) = uint16(squeeze(mean(mean(reshape(rawData(1:h.m.height,1:h.m.width,indexx.(h.m.LEDs{k}){j}),[h.m.dsf,h.m.height/h.m.dsf,h.m.dsf,h.m.height/h.m.dsf,numel(indexx.(h.m.LEDs{k}){j})]),3),1))) - repmat(imresize(data.bkg.(h.m.LEDs{k}),1/h.m.dsf),[1 1 numel(indexx.(h.m.LEDs{k}){j})]);
            else
                data.(h.m.LEDs{k})(:,:,dsindex.(h.m.LEDs{k}){j}) = rawData(1:h.m.height,1:h.m.width,indexx.(h.m.LEDs{k}){j})-repmat(data.bkg.(h.m.LEDs{k}),[1 1 numel(indexx.(h.m.LEDs{k}){j})]);
            end
        end

        if mod(j,10)
            if h.m.isgui
                h.status.String = sprintf('\n\n %i %% complete',round(j*100/length(filesToLoad))); drawnow
            else
                try
                    textprogressbar(round(j*100/length(filesToLoad)));
                catch
                    textprogressbar(sprintf(['Loading ' h.m.mouse ' ' h.m.run ' stim ' mat2str(h.m.stim) '\r']))
                end
            end
        end
    end

    textprogressbar(sprintf('  Done'))

elseif strcmp(h.m.camera,'none')
    data = 'No Data loaded';
    return
end
try
    ss = size(data.(h.m.LEDs{1}));
catch
end
% Rotate
if isfield(h.m,'nrot') && ~isempty(regexp(h.m.outputs,'[rgblodn]'))
    for i = 1:h.m.nLEDs
        data.(h.m.LEDs{i}) = rot90(data.(h.m.LEDs{i}),h.m.nrot);
    end
    disp('Rotated data')
end

% autocrop
if h.m.autocrop
    disp('autocropping...')
    tmp = reshape(data.(h.m.LEDs{1}),[h.m.height*h.m.width/(h.m.dsf^2), size(data.(h.m.LEDs{1}),3)]);
    for i = 1:size(tmp,1)
        [~,croptst(i)] = runstest(tmp(i,:));
    end
    croptst(croptst < .00001) = 0;
    croptst(croptst > .00001) = 1;
    croptst = ~logical(reshape(croptst,[h.m.height/h.m.dsf h.m.width/h.m.dsf]));
    h.m.BW = imerode(croptst,ones(4));
end

% apply mask
if isfield(h.m,'BW')  && ~isempty(regexp(h.m.outputs,'[rgblodn]'))
    for i = 1:h.m.nLEDs
        data.(h.m.LEDs{i}) = data.(h.m.LEDs{i}).*repmat(imresize(h.m.BW,ss(1:2)),[1 1 size(data.(h.m.LEDs{i}),3)]);
    end
    disp('Cropped data')
elseif ~isempty(regexp(h.m.outputs,'[rgblodn]'))
    qans = questdlg('No crop mask found. Would you like to create one?','Yes','No');
    if strcmp(qans,'Yes')
        tmp = figure;
        if isfield(data,'blue')
            imagesc(std(data.blue,[],3))
        else
            imagesc(std(data.lime,[],3))
        end
        axis image
        h.m.BW = roipoly;
        close(tmp)
        for i = 1:h.m.nLEDs
            data.(h.m.LEDs{i}) = data.(h.m.LEDs{i}).*repmat(imresize(h.m.BW,ss(1:2)),[1 1 size(data.(h.m.LEDs{i}),3)]);
        end
    end
end

if ~isempty(h.m.corr_flicker)
    for i = h.m.corr_flicker
        disp(['Flicker ' h.m.LEDs{i}])
        flkcor = squeeze(nanmean(nanmean(data.(h.m.LEDs{i}),2),1));
        if strcmp(h.m.LEDs{i},'red') || strcmp(h.m.LEDs{i},'green')
            corfact(1,1,:) = nanmean(flkcor)+flkcor-smooth(flkcor,floor(h.m.framerate/6)*2+1);
        else
            corfact(1,1,:) = nanmean(flkcor)+flkcor-smooth(flkcor,floor(h.m.framerate/12)*2+1);
        end
        data.(h.m.LEDs{i}) = nanmean(corfact)*data.(h.m.LEDs{i})./repmat(corfact,[ss(1),ss(2),1]);
    end
end

if isfield(h.m,'corr_flicker_exp')
    for i = h.m.corr_flicker_exp
        disp(['Flicker ' h.m.LEDs{i}])
        tc = squeeze(nanmean(nanmean(data.(h.m.LEDs{i}),2),1));
        [~,facty]= flkcor_beth_glob(tc',data.(h.m.LEDs{i}),0);
        facty = reshape(facty,[1 1 numel(facty)]);
        tc = reshape(tc,[1 1 numel(tc)]);
        data.(h.m.LEDs{i}) = data.(h.m.LEDs{i}).*repmat(tc,[ss(1) ss(1) 1]);
    end
end

if ~isempty(h.m.smooth)
    for i = h.m.smooth
        disp(['Smoothing ' h.m.LEDs{i}])
        data.(h.m.LEDs{i}) = smooth3(data.(h.m.LEDs{i}),'box',[1 1 3]);
    end
end

if h.m.PCAcomps > 0  && ~isempty(regexp(h.m.outputs,'[rgblodnP]'))
    for i = 1:h.m.nLEDs
        disp(['PCA ' h.m.LEDs{i}])
        tmp = reshape(data.(h.m.LEDs{i}),[ss(1)*ss(2),ss(3)]);
        h.m.nanidx = isfinite(tmp(:,1));% non nan indice
        [data.C.(h.m.LEDs{i}),data.S.(h.m.LEDs{i}),data.expl.(h.m.LEDs{i})] = fsvd(tmp(h.m.nanidx,:),h.m.PCAcomps,2,1);
        expl = cumsum(data.expl.(h.m.LEDs{i}));
        [h.m.kneept, ~] = knee_pt(expl,1:numel(expl),1);
        disp(['Knee point at ' mat2str(h.m.kneept)])
        if ~isempty(regexp(h.m.outputs,'[rgblodn]'))
            tmp(h.m.nanidx,:) = data.C.(h.m.LEDs{i})*data.S.(h.m.LEDs{i});
            data.(h.m.LEDs{i}) = reshape(tmp,ss);
        end
    end
end
clear COEFF SCORE

if ~isempty(regexp(h.m.outputs,'[1]'))
    WFL = dir(fullfile(h.m.ccddir, '**', ['*' h.m.run '_stim' h.m.stim '_cam1.avi']));
    disp('Loading Webcam 1...')
    if isempty(WFL)
        data.webcam1 = LoadWebcamJPG(fullfile(h.m.CCDdir,h.m.run,[h.m.run '_webcam' h.m.stim]),h.m.dsf);
    else
        [data.webcam1,h.m] = LoadWebcamAVI(fullfile(WFL.folder,WFL.name),h.m);
    end
    disp('Done loading webcam 1')
end

if ~isempty(regexp(h.m.outputs,'[2]'))
    WFL = dir(fullfile(h.m.ccddir, '**', ['*' h.m.run '_stim' h.m.stim '_cam2.avi']));
    disp('Loading Webcam 2...')
    if isempty(WFL)
        data.webcam2 = LoadWebcamJPG(fullfile(strrep(h.m.CCDdir,'CCD','stimCCD'),[h.m.run 'stim' mat2str(h.m.stim) '_webcam']));
    else
        [data.webcam2,h.m] = LoadWebcamAVI(fullfile(WFL.folder,WFL.name),h.m);
    end
    disp('Done loading Webcam 2')
end

if ~isempty(regexp(h.m.outputs,'[R]'))
    [data.rotary,h.m] = LoadRotary(fullfile(h.m.CCDdir,h.m.run,[h.m.run '_stim' mat2str(h.m.stim) '_rotary.txt']),h.m);
    disp('Done loading rotary')
end

if ~isempty(regexp(h.m.outputs,'[odn]'))
    disp('Converting Hemodynamics...')
    [data.chbo,data.chbr,~] = convert_mariel_MIAO(data.green,data.red,'g','r',h.m.baseline,534);
    h.m.conv_vars = {'chbo','chbr'};
end

if ~isempty(regexp(h.m.outputs,'[n]'))
    if isfield(data,'blue')
        disp('Converting GCaMP...')
        data.gcamp = GcampMcCorrection_MIAO(data.blue,data.chbr,data.chbo,h.m.baseline,h.m.dpf(1),h.m.dpf(2));
        h.m.conv_vars = [h.m.conv_vars 'gcamp'];
    elseif isfield(data,'lime')
        disp('Converting jRGECO...')
        h.m.bkg = 90; % PLACEHOLDER
        data.jrgeco = (data.lime-h.m.bkg)./((abs(data.red-h.m.bkg).^h.m.Dr).*(abs(data.green).^h.m.Dg));
        h.m.bgGG = mean(data.jrgeco(:,:,h.m.baseline),3);
        data.jrgeco = data.jrgeco./repmat(h.m.bgGG,[1 1 size(data.jrgeco,3)])-1;
        h.m.conv_vars = [h.m.conv_vars 'jrgeco'];
    end
end

if ~h.m.isgui
    opts = 'rgblodnn';
    fields = {'red','green','blue','lime','chbo','chbr','gcamp','jrgeco'};
    for i = 1:length(opts)
        if isempty(regexp(h.m.outputs,opts(i)))
            try
                data = rmfield(data,fields{i});
            catch
            end
        end
    end
end
m = h.m;
disp('Done')

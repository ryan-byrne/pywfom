cameraBinFactor = 1;
​
disp('LOADING METADATA')
% Creates file path of zyla metadata file (.ini)
zylaInfoFilePath = fullfile(pwd, 'acquisitionmetadata.ini');
FID = fopen(zylaInfoFilePath, 'r');
zylaMetaData = fread(FID, '*char')';
fclose(FID);
​
​
numDepths = str2double(zylaMetaData(12+(strfind(zylaMetaData, 'AOIHeight = ')):(strfind(zylaMetaData, 'AOIWidth = ')-1)));
numLatPix = str2double(zylaMetaData((11+strfind(zylaMetaData, 'AOIWidth = ')):(strfind(zylaMetaData, 'AOIStride = ')-1)));
imageBytes = str2double(zylaMetaData((17+strfind(zylaMetaData, 'ImageSizeBytes = ')):(strfind(zylaMetaData, '[multiimage]')-1)));
numFramesPerSpool = str2double(zylaMetaData((16+strfind(zylaMetaData, 'ImagesPerFile = ')):end));
startIndex = strfind(zylaMetaData, 'ImageSizeBytes') + length('ImageSizeBytes = ');
ImageSize = str2double(zylaMetaData(startIndex : startIndex + 7));
​
​
​
% add extra columns for 2 buffer rows (why?)
if (2 == cameraBinFactor)
    numColumns = numDepths + 1;
    numRows = ImageSize / 2 / numColumns;
    if(mod(numRows, 1) ~= 0)
        numColumns = numDepths+2;
        numRows = ImageSize/2/numColumns;
    end
else
    numColumns = numDepths+2;
    numRows = numLatPix;
end
​
numSpoolFiles = length(dir)-5;
numFramesAcquired = numSpoolFiles*numFramesPerSpool;
​
% Creates a list of spool file names that exist for a given run
disp('CREATING SPOOL FILE NAMES')
spoolCounter=0;
for i = 1:floor(numFramesAcquired/(numFramesPerSpool))
    spoolCounter=spoolCounter+1;
    temp = i;
    for j = 1:10
        a(i, j) = mod(temp, 10^j)/(10^(j-1));
        temp = temp-mod(temp, 10^j);
    end
    tempName = mat2str(a(i, :));
    tempName = tempName(2:end-1);
    tempName = tempName(find(tempName ~= ' '));
    tempName = [tempName 'spool.dat'];
    namesOut{spoolCounter} = tempName;
end
namesOut = [{'0000000000spool.dat'} namesOut];
filesToLoad = namesOut
clear namesOut tempName temp a spoolCounter
SCAPE_data = zeros(numRows, numColumns, numFramesPerSpool*numSpoolFiles, 'uint16');
​
for i = 1:numSpoolFiles
   fileToLoad = filesToLoad{1};
   fid = fopen(fileToLoad);
   A = fread(fid, 'uint16=>uint16');
   indices = [(numFramesPerSpool*(i-1))+1:numFramesPerSpool*i];
   SCAPE_data(:, :, indices) = reshape(A, [numRows, numColumns, numFramesPerSpool]);
   i
end

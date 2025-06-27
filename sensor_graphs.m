%% Setup workspace
clc; clear; close all;

%% Jobs needed 
jobs = {
    '/Users/teresanguyen/Documents/Faboratory Stuff/soft-robotics-simulations/sensor_062325/rhand_062325.csv',          'Right Hand Sensor Data: 06/23/2025',              '/Users/teresanguyen/Documents/Faboratory Stuff/soft-robotics-simulations/sensor_062325/figures/rhand_sensor_062325.jpg';
    '/Users/teresanguyen/Documents/Faboratory Stuff/soft-robotics-simulations/sensor_062325/lhand_sensor_062325.csv',    'Left Hand Sensor Data: 06/23/2025',               '/Users/teresanguyen/Documents/Faboratory Stuff/soft-robotics-simulations/sensor_062325/figures/lhand_sensor_062325.jpg';
    '/Users/teresanguyen/Documents/Faboratory Stuff/soft-robotics-simulations/sensor_062325/apose_sensor_062325.csv',    'Apose Sensor Data: 06/23/2025',                   '/Users/teresanguyen/Documents/Faboratory Stuff/soft-robotics-simulations/sensor_062325/figures/apose_sensor_062325.jpg';
    '/Users/teresanguyen/Documents/Faboratory Stuff/soft-robotics-simulations/sensor_062325/double_lat_sensor_062325.csv','Double Lateral Sensor Data: 06/23/2025',        '/Users/teresanguyen/Documents/Faboratory Stuff/soft-robotics-simulations/sensor_062325/figures/double_lat_sensor_062325.jpg';
    '/Users/teresanguyen/Documents/Faboratory Stuff/soft-robotics-simulations/sensor_062325/rhand_long_sensor_062325.csv','Right Hand Long Sensor Data: 06/23/2025',    '/Users/teresanguyen/Documents/Faboratory Stuff/soft-robotics-simulations/sensor_062325/figures/rhand_long_sensor_062325.jpg';
    '/Users/teresanguyen/Documents/Faboratory Stuff/soft-robotics-simulations/sensor_062325/rhand_long_fast_sensor_062325.csv','Right Hand Long Fast Sensor Data: 06/23/2025','/Users/teresanguyen/Documents/Faboratory Stuff/soft-robotics-simulations/sensor_062325/figures/rhand_long_fast_sensor_062325.jpg';
    '/Users/teresanguyen/Documents/Faboratory Stuff/soft-robotics-simulations/sensor_062325/lhand_long_sensor_062325.csv','Left Hand Long Sensor Data: 06/23/2025',      '/Users/teresanguyen/Documents/Faboratory Stuff/soft-robotics-simulations/sensor_062325/figures/lhand_long_sensor_062325.jpg';
    '/Users/teresanguyen/Documents/Faboratory Stuff/soft-robotics-simulations/sensor_062325/lhand_long_fast_sensor_062325.csv','Left Hand Long Fast Sensor Data: 06/23/2025','/Users/teresanguyen/Documents/Faboratory Stuff/soft-robotics-simulations/sensor_062325/figures/lhand_long_fast_sensor_062325.jpg';
    '/Users/teresanguyen/Documents/Faboratory Stuff/soft-robotics-simulations/sensor_062325/bending_back_long_sensor_062325.csv','Bending Back Long Sensor Data: 06/23/2025','/Users/teresanguyen/Documents/Faboratory Stuff/soft-robotics-simulations/sensor_062325/figures/bending_back_long_sensor_062325.jpg';
    '/Users/teresanguyen/Documents/Faboratory Stuff/soft-robotics-simulations/sensor_062325/double_lat_long_sensor_062325.csv','Double Lateral Long Sensor Data: 06/23/2025','/Users/teresanguyen/Documents/Faboratory Stuff/soft-robotics-simulations/sensor_062325/figures/double_lat_long_sensor_062325.jpg';
    '/Users/teresanguyen/Documents/Faboratory Stuff/soft-robotics-simulations/sensor_062325/lhand_slow_sensor_062325.csv','Left Arm Slow Data: 06/23/2025',              '/Users/teresanguyen/Documents/Faboratory Stuff/soft-robotics-simulations/sensor_062325/figures/lhand_slow_sensor_062325.jpg';
    '/Users/teresanguyen/Documents/Faboratory Stuff/soft-robotics-simulations/sensor_062325/rhand_slow_sensor_062325.csv','Right Arm Slow Data: 06/23/2025',             '/Users/teresanguyen/Documents/Faboratory Stuff/soft-robotics-simulations/sensor_062325/figures/rhand_slow_sensor_062325.jpg';
};

% change col names
col_list = {
    'Right shoulder (back)'
    'Right shoulder (front)'
    'Right collarbone'
    'Middle of back'
    'Top of back'
    'Left collarbone'
    'Left shoulder (front)'
    'Left armpit (back)'
    'Left shoulder (back)'
    'Left arm (back)'
    'Left armpit (front)'
    'Waist left a'
    'Chest l (middle)'
    'Stomach l'
    'Waist left c'
    'Waist left b'
    'Right armpit (back)'
    'Right arm (back)'
    'Right armpit (front)'
    'Waist right a'
    'Waist right b'
    'Waist right c'
    'Stomach r'
    'Chest r'
};


%% Loop over jobs
for k = 1:size(jobs,1)
    infile   = jobs{k,1};
    figTitle = jobs{k,2};
    outjpg   = jobs{k,3};  
    
    % preparation/rename columns
    T = readtable(infile);
    assert(width(T) == numel(col_list), ...
           'Column count mismatch: %d in table vs %d in col_list', ...
           width(T), numel(col_list));

    T.Properties.VariableNames = matlab.lang.makeValidName(col_list);
    
    data     = T{:,:};
    varNames = T.Properties.VariableNames;
    nPlots   = size(data,2);
    nRows    = ceil(sqrt(nPlots));
    nCols    = ceil(nPlots / nRows);
    
    % figure creation
    figure;
    set(gcf, 'Units','Normalized','OuterPosition',[0 0 1 1]);
    for i = 1:nPlots
        ax = subplot(nRows, nCols, i);
        plot(data(:,i), 'LineWidth', 1.2);
        grid(ax,'on');
        xlabel(ax,'Row #');
        ylabel(ax,'Cap (F)');
        title(ax, varNames{i}, 'Interpreter','none');
    end
    
    % change title & file 
    sgtitle(figTitle);

    if ~isempty(outjpg)
        saveas(gcf, outjpg);
    end
end

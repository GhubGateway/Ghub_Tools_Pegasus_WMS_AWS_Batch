%--------------------------------------------------------------------------------
% consume_lunch_items.m
% Component of:
%     https://github.com/GhubGateway/Ghub_Pegasus_WMS_Tutorial_and_Templates and
%     https://theghub.org/tools/ghubex1
% Called from: Octave_Launch.sh
% Also see Ghub, https://theghub.org/about
%--------------------------------------------------------------------------------

% In the Pegasus WMS YAML file,
% this job is specified to have the f.b input file and the f.c output file

function main()

    if nargin < 1
      a = argv();
      job_index = a{end};
    end

    % f.b contains the served lunch items

    fp1 = fopen ('f.b', 'r');
    fp2 = fopen ('f.c', 'w');

    served_lunch_items = fgetl(fp1);
    fprintf(fp2, '%s Job index: %s. Consumed lunch items! Thank you for lunch. Yum Yum!!', served_lunch_items, job_index);

    fclose (fp1);
    fclose (fp2);

    % f.c contains the thank you note
   
end

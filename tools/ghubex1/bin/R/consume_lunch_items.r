#--------------------------------------------------------------------------------
# consume_lunch_items.r
# Component of:
#     https://github.com/GhubGateway/Ghub_Pegasus_WMS_Tutorial_and_Templates and
#     https://theghub.org/tools/ghubex1
# Called from: R_Launch.sh
# Also see Ghub, https://theghub.org/about
#--------------------------------------------------------------------------------

# In the Pegasus WMS YAML file,
# this job is specified to have the f.b input file and the f.c output file

main <- function(argv) {
    
    job_index <- argv[1]
  
    # f.b contains the served lunch items

    fp1 <- file('f.b', 'r')
    fp2 <- file('f.c', 'w')

    served_lunch_items <- readLines(fp1, n=1)
    writeLines(sprintf('%s Job index: %s. Consumed lunch items! Thank you for lunch. Yum Yum!!', served_lunch_items, job_index), fp2)
    
    close(fp1)
    close(fp2)

    # f.c contains the thank you note
}

# Execute main function
main(commandArgs(trailingOnly = TRUE))


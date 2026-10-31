#--------------------------------------------------------------------------------
# receive_lunch_items.r
# Component of:
#     https://github.com/GhubGateway/Ghub_Pegasus_WMS_Tutorial_and_Templates and
#     https://theghub.org/tools/ghubex1
# Called from: R_Launch.sh
# Also see Ghub, https://theghub.org/about
#--------------------------------------------------------------------------------

# In the Pegasus WMS YAML file,
# this job is specified to have the f.a input file and the f.b output file

main <- function(argv) {
  
  job_index <- argv[1]
  
  # f.a contains the received lunch items
  
  fp1 <- file('f.a', 'r')
  fp2 <- file('f.b', 'w')
  
  received_lunch_items <- readLines(fp1, n=1)
  writeLines(sprintf('Job index: %s. Received lunch items: %s.', job_index, received_lunch_items), fp2)
  
  close(fp1)
  close(fp2)
  
  # f.b contains the served lunch items
}

# Execute main function
main(commandArgs(trailingOnly = TRUE))

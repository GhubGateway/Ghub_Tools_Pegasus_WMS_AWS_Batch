!--------------------------------------------------------------------------------
! consume_lunch_items.f90
! Component of:
!     https://github.com/GhubGateway/Ghub_Pegasus_WMS_Tutorial_and_Templates and
!     https://theghub.org/tools/ghubex1
! Executable called from: Fortran_Launch.sh
! Also see Ghub, https://theghub.org/about
!--------------------------------------------------------------------------------

! In the Pegasus WMS YAML file,
! this job is specified to have the f.b input file and the f.c output file

program consume_lunch_items
    
    integer,parameter :: MAXSTRLEN=512
    CHARACTER(LEN=MAXSTRLEN) :: job_index, served_lunch_items

    call getarg(1, job_index)

    ! f.b contains the served lunch items

    open(1, file='f.b', status='old')
    open(2, file='f.c', status='replace')
    
    read(1,'(A)') served_lunch_items
    ! gfortran stops reading a free-form line at column 132, or at column 72 in fixed-form
    write(2,'(4A)') trim(served_lunch_items), 'Job index: ', trim(job_index), &
        '. Consumed lunch items! Thank you for lunch. Yum Yum!!'
 
    close(1)
    close(2)
    
    ! f.c contains the thank you note

END program consume_lunch_items

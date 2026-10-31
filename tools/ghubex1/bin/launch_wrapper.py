 #---------------------------------------------------------------------------------------------------
# launch_wrapper.py
# Component of:
#     https://github.com/GhubGateway/Ghub_Pegasus_WMS_Tutorial_and_Templates and
#     https://theghub.org/tools/ghubex1
# Called from: ghubex1.ipynb
# Also see Ghub, https://theghub.org/about
# Purpose: Plan and submit a Pegasus WMS workflow
# Author: Renette Jones-Ivey
# Date: July 2026
# Reference: https://pegasus.isi.edu/documentation
#---------------------------------------------------------------------------------------------------

import ast
import boto3
import datetime
import logging
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
#from datetime import datetime

import hublib.cmd
#help (hublib.cmd.command.executeCommand)

# API for generating Pegasus YAML files
from Pegasus.api import *

# Configuration parameters
import configuration as cfg

class LaunchWrapper():
    
    def __init__(self, template_index, user, lunch_items):

        # Create a logger
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)

        self.logger = logger
        self.workingdir = '.'
        self.bindir ='.'
        self.scriptsdir = './pegasus-wms-scripts'
        self.datadir = '.'
        self.examplesdir = '.'
        self.workflow_results_directory = os.path.join('.', 'LOCAL', 'shared-storage')
        self.num_simulations = 1
        self.maxwalltime = 10 #min
        self.template_index = template_index
        self.user = user
        self.lunch_items = lunch_items
 
        '''
        print('self.template_index: ', self.template_index)
        print('self.user: ', self.user)
        print('self.lunch_items: ', self.lunch_items)
        '''

    def display_output (self, message):
        print (message)
        self.logger.info (message)
                
    def subprocess_popen (self, subprocess_args):

        #https://stackoverflow.com/questions/21953835/run-subprocess-and-print-output-to-logging
        #https://stackoverflow.com/questions/5631624/how-to-get-exit-code-when-using-python-subprocess-communicate-method
        subprocess_result = subprocess.Popen(subprocess_args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        #print ('type(subprocess_result): ', type(subprocess_result)) #<class 'subprocess.Popen'>
        subprocess_output, _ =  subprocess_result.communicate() # Wait for and communicate output
        returncode = subprocess_result.returncode
        #print ('type(subprocess_output): ', type(subprocess_output)) #<class 'bytes'>
        #print ("type(returncode): ", type (returncode)) #<class 'int'>
        decoded_string = subprocess_output.decode('utf-8')  # Or the appropriate encoding
        lines = decoded_string.splitlines()
        for line in lines:
            print(line)
        return returncode
    
    # VPCs are assigned for regions.
    def get_subnet_info(self, vpc):
        
        subnets_dict = self.boto3_ec2_client.describe_subnets(
            Filters=[{'Name': 'vpc-id', 'Values': [vpc]}]
        )
        #keys = [x for x in subnets_dict]
        #print(keys)
        # ['Subnets', 'ResponseMetadata']
        #print (subnets_dict)
        #log_info ('subnets_dict: %s' %str(subnets_dict))
        subnets = [ sub['SubnetId'] for sub in subnets_dict['Subnets']]
        print('subnets: ', subnets)
        self.subnet = subnets[0]
        #subnet.options = subnets
        #subnet.value = subnets[0]
    
    def get_security_group_info(self, vpc):
        
        security_groups_dict = self.boto3_ec2_client.describe_security_groups(
            Filters=[{'Name': 'vpc-id', 'Values': [vpc]}]
        )
        #keys = [x for x in security_groups_dict]
        #print(keys)
        # ['SecurityGroups', 'ResponseMetadata']
        #print (security_groups_dict)
        #log_info ('security_groups_dict: %s' %str(security_groups_dict))
        security_groups = [ sub['GroupId'] for sub in security_groups_dict['SecurityGroups']]
        print('security_groups: ', security_groups)
        self.security_group = security_groups[0]
        #security_group.options = security_groups
        #security_group.value = security_groups[0]
        
    def get_vpc_info(self):

        vpcs_dict = self.boto3_ec2_client.describe_vpcs()
        #keys = [x for x in vpcs_dict]
        #print(keys)
        # ['Vpcs', 'ResponseMetadata']
        #print (vpcs_dict)
        #log_info ('vpcs_dict: %s' %str(vpcs_dict))
    
        #keys = [x for x in vpcs_dict]
        #print(keys)
        # ['Vpcs', 'ResponseMetadata']
    
        vpcs = [ sub['VpcId'] for sub in vpcs_dict['Vpcs']]
        print('vpcs: ', vpcs)
        
        #vpc.options = vpcs
        #vpc.value = vpcs[0]
    
        self.get_subnet_info(vpcs[0])
        self.get_security_group_info(vpcs[0])
        
    def run_workflow(self):

        try:
        
            template =  cfg.TEMPLATE_LIST[self.template_index]
            self.display_output(f'Configuring the workflow for template: {template}...')

            # Update pegasus aws batch configuration files.
            # TODO: update based on user selected parameters.
            self.memory = 600 #MiB
            self.aws_region = 'us-east-1'
            self.boto3_session = boto3.session.Session()
            self.boto3_iam_client = boto3.client('iam')
            self.boto3_ec2_client = boto3.client('ec2')

            iam_user_dict = self.boto3_iam_client.get_user()
            print ('iam_user_dict: ', iam_user_dict)
            keys = [x for x in iam_user_dict]
            print(keys)
            ['User', 'ResponseMetadata']
            self.aws_iam_username = iam_user_dict['User']['UserName']
            print ('self.aws_iam_username: ', self.aws_iam_username)
            self.get_vpc_info()
 
            ########################################################################
            # Create the TOPDIR, PEGASUS_LOCAL_BIN_DIR, S3_URL_PREFIX, S3_BUCKET, and S3_BUCKET_KEY
            # environment variables for ./conf/sites.xml.
            ########################################################################
 
            TOPDIR = os.getcwd()
            os.environ['TOPDIR'] = TOPDIR
            self.logger.info("os.environ['TOPDIR']: %s" %str(os.environ['TOPDIR']))
            os.environ["CONDOR_CONFIG"] = "/etc/condor/condor_config"             
            self.logger.info("os.environ['CONDOR_CONFIG']: %s" %str(os.environ['CONDOR_CONFIG']))

            #BIN_DIR=`pegasus-config --bin`
            #echo "BIN_DIR: "$BIN_DIR
            #PEGASUS_LOCAL_BIN_DIR=${BIN_DIR}
            #export PEGASUS_LOCAL_BIN_DIR
            PEGASUS_LOCAL_BIN_DIR = '/usr/bin'
            os.environ['PEGASUS_LOCAL_BIN_DIR'] = PEGASUS_LOCAL_BIN_DIR
            self.logger.info("os.environ['PEGASUS_LOCAL_BIN_DIR']: %s" %str(os.environ['PEGASUS_LOCAL_BIN_DIR']))
            
            S3_URL_PREFIX = 's3://user@amazon'
            os.environ['S3_URL_PREFIX'] = S3_URL_PREFIX
            self.logger.info("os.environ['S3_URL_PREFIX']: %s" %str(os.environ['S3_URL_PREFIX']))
            
            # ./pegasusrc sets pegasus.catalog.site.file=./conf/sites.xml.
            # ./conf/sites.xml aws-batch site's file server definition sets url to "${S3_URL_PREFIX}/${S3_BUCKET}/${S3_BUCKET_KEY}"
            # The globally unique S3_BUCKET is created by Pegasus (if it does not already exist), for the current Amazon AWS Partition and IAM user.
            # See https://docs.aws.amazon.com/AmazonS3/latest/userguide/bucketnamingrules.html for more information on bucket naming rules.
            bucket_name_suffix = re.sub(r'[^a-zA-Z0-9]+', '', str(self.aws_region + self.aws_iam_username)).lower()[:63]
            S3_BUCKET = 'pegasus-scratch-%s' %bucket_name_suffix
            #print ('S3_BUCKET: ', S3_BUCKET)
            os.environ['S3_BUCKET'] = S3_BUCKET
            self.logger.info("os.environ['S3_BUCKET']: %s" %str(os.environ['S3_BUCKET']))
            # The S3_BUCKET_KEY (i.e. directory) is created for each workflow run and deleted after each workflow run.
            S3_BUCKET_KEY = 'ghub_workflow'
            #print ('S3_BUCKET_KEY: ', S3_BUCKET_KEY)
            os.environ['S3_BUCKET_KEY'] = S3_BUCKET_KEY
            self.logger.info("os.environ['S3_BUCKET_KEY']: %s" %str(os.environ['S3_BUCKET_KEY']))

            ########################################################################
            # Create and plan the Pegasus WMS workflow
            ########################################################################

            workflow_name = 'ghub_workflow_jobs'
            #print ('workflow_name: ', workflow_name)
            wf = Workflow(workflow_name)
            #print ('wf: ', wf)

            # Pegasus requires three catalogs and the workflow's job definitions to plan and start a workflow.
            # The site catalog defines the site(s) where the workflow jobs are to be executed.
            sc = SiteCatalog()
            wf.add_site_catalog(sc)
            # The transformation catalog defines the executable(s) invoked on the cluster to run the workflow jobs.
            tc = TransformationCatalog()
            wf.add_transformation_catalog(tc)
            # The replica catalog defines the locations of the input files required by the workflow jobs.
            rc = ReplicaCatalog()
            wf.add_replica_catalog(rc)
    
            ########################################################################
            # Configure the site catalog
            ########################################################################

            # Local Host PC Site (Where Pegasus planner & HTCondor run)
            local_scratch = os.path.join(TOPDIR, "LOCAL", "shared-svratch")
            local_storage = os.path.join(TOPDIR, "LOCAL", "shared-storage")
            
            local = Site("local", arch=Arch.X86_64, os_type=OS.LINUX)
            local.add_directories(
                Directory(Directory.SHARED_SCRATCH, local_scratch).add_file_servers(
                    FileServer("file://" + local_scratch, Operation.ALL)
                ),
                Directory(Directory.SHARED_STORAGE, local_storage).add_file_servers(
                    FileServer("file://" + local_storage, Operation.ALL)
                ),
            )
            local.add_env(PEGASUS_HOME=os.path.normpath(os.path.join(PEGASUS_LOCAL_BIN_DIR, "..")))
            local.add_pegasus_profile(clusters_num=1)
            
            # Remote Amazon AWS Batch Execution Site
            aws = Site("aws-batch", arch=Arch.X86_64, os_type=OS.LINUX)
            aws.add_directories(
                # The API requires an absolute path, so the bucket path gets a leading "/"
                Directory(Directory.SHARED_SCRATCH, f"/{S3_BUCKET}/{S3_BUCKET_KEY}").add_file_servers(
                    FileServer(f"{S3_URL_PREFIX}/{S3_BUCKET}/{S3_BUCKET_KEY}", Operation.ALL)
                )
            )
            aws.add_pegasus_profile(clusters_num=1, style="condor")
            # aws.add_condor_profile(universe="local")
            
            sc.add_sites(local, aws)
            sc.write("sites.yml")
            print("Wrote sites.yml")
            
            ########################################################################
            # Configure the transformation catalog
            ########################################################################

            tooldir = os.path.dirname(os.path.dirname(os.path.realpath(os.path.abspath(__file__))))
            #print ('tooldir: ', tooldir)
            workingdir = os.getcwd()
            #print ('workingdir: ', workingdir)
            
            # Add the build script to the Transformation Catalog.
            # The build script contains specific instructions for compiling the executable.

            if cfg.BIN_LISTS[0][self.template_index] != None:
                
                build_exec_path =  os.path.join(tooldir, 'remotebin', template, '%s_Build.sh' %template)
                self.logger.info ('build_exec_path: %s' %build_exec_path)
                
                build_exec = Transformation(
                    '%sBuild' %template,
                    site='local',
                    pfn=build_exec_path,
                    is_stageable = True, #Stageable or installed
                    arch = Arch.X86_64,
                    os_type = OS.LINUX,
                )
                tc.add_transformations(build_exec)
     
            # Add the launch script to the Transformation Catalog.
             
            launch_exec_path =  os.path.join(workingdir, 'remotebin', template, '%s_Launch.sh' %template)
            print ("launch_exec_path: %s" %launch_exec_path)
            
            launch_exec = Transformation(
                '%sLaunch' %template,
                site='local',
                pfn=launch_exec_path,
                is_stageable = True, #Stageable or installed
                arch=Arch.X86_64,
                os_type=OS.LINUX)
            tc.add_transformations(launch_exec)
            
            ########################################################################
            # Add jobs to the workflow and configure the replica catalog as required
            ########################################################################

            # PFNs:

            # All files in a Pegasus workflow are referred to in the DAX using their Logical File Name (LFN).
            # These LFNs are mapped to Physical File Names (PFNs) when Pegasus plans the workflow.
            # Add input files to the DAX-level replica catalog.
            # On Ghub, .add_outputs register_replica must be set to False (the default is True) to prevent
            # Pegasus from returning with a post script failure.

            # Create the f.a input file for the receive workflow job
            
            f_a_filepath = os.path.join(workingdir, 'f.a')
            self.logger.info('f_a_filepath: %s' %f_a_filepath)
            fp = open(f_a_filepath,'w')
            if fp:
               fp.write('{0}\n'.format(self.lunch_items.rstrip()))
               fp.close()
            else:
               self.logger.error ('Could not create the %s input file.\n' %f_a_filepath)
               return 1
            input_list = ['f.a', 'f.b']
            output_list = ['f.b','f.c']
            rc.add_replica('local', File('f.a'), f_a_filepath)

            src_dir =  os.path.join(tooldir, 'bin', template)
            bin_dir =  os.path.join(tooldir, 'bin', template)

            for i in range(cfg.NUM_LISTS):
 
                src_filename = cfg.SRC_LISTS[i][self.template_index]
                src_filepath = os.path.join(src_dir, src_filename)
                bin_filename = cfg.BIN_LISTS[i][self.template_index]

                if (bin_filename == None): 

                    # Copy the job script to the scratch directory
                    rc.add_replica('local', File(src_filename), src_filepath)
                    exec_job = Job(launch_exec)\
                        .add_args("""./%s %s""" %(src_filename, str(i)))\
                        .add_inputs(File(src_filename))\
                        .add_inputs(File(input_list[i]))\
                        .add_outputs(File(output_list[i]), stage_out=True, register_replica=False)\
                        .add_metadata(time='%d' %self.maxwalltime)
                    wf.add_jobs(exec_job)

                else:
                    
                    bin_filepath = os.path.join(bin_dir, bin_filename)
                   
                    if os.path.exists(bin_filepath) and Path(src_filepath).stat().st_mtime < Path(bin_filepath).stat().st_mtime:
    
                        rc.add_replica('local', File(bin_filename), bin_filepath)
                        exec_job = Job(launch_exec)\
                            .add_args("""./%s %s""" %(bin_filename, str(i)))\
                            .add_inputs(File(bin_filename))\
                            .add_inputs(File(input_list[i]))\
                            .add_outputs(File(output_list[i]), stage_out=True, register_replica=False)\
                            .add_metadata(time='%d' %self.maxwalltime)
                        wf.add_jobs(exec_job)
    
                    else:

                        rc.add_replica('local', File('%s' %src_filename), src_filepath)
                        build_job = Job(build_exec)\
                        	.add_args("""%s %s""" %(src_filename, bin_filename))\
                        	.add_inputs(File(src_filename))\
                        	.add_outputs(File(bin_filename), stage_out=True, register_replica=False)\
                            .add_metadata(time='%d' %self.maxwalltime)
                        wf.add_jobs(build_job)
                        exec_job = Job(launch_exec)\
                        	.add_args("""./%s %s""" %(bin_filename, str(i)))\
                            .add_inputs(File(bin_filename))\
                        	.add_inputs(File(input_list[i]))\
                        	.add_outputs(File(output_list[i]), stage_out=True, register_replica=False)\
                        	.add_metadata(time='%d' %self.maxwalltime)
                        wf.add_jobs(exec_job)
                        wf.add_dependency(exec_job, parents=[build_job])
                 
                if i==0:
                    parent_exec_job = exec_job
                else:
                    wf.add_dependency(exec_job, parents=[parent_exec_job])
  
            ########################################################################
            # Create the YAML (YAML Ain't Markup Language) file
            ########################################################################

            try:
                wf.write('workflow.yml')
            except PegasusClientError as e:
                self.logger.error(str(e))
                return 1

            # Verify contents
            #fp = open('workflow.yml', 'r')
            #file_contents = fp.read()
            #print (file_contents)
            #fp.close()
            
            sys.stdout.flush()

            utcnow = datetime.datetime.utcnow().strftime('%Y%m%d%H%M%S%f')
            prefix = 'remotehost-' + utcnow
            print ('prefix: %s' %prefix)

            ########################################################################
            # Submit the Pegasus Workflow plan
            ########################################################################

            try:

                script_path = os.path.join(self.scriptsdir,"pegasus-aws-batch-configure.sh")
                self.logger.info ('Calling %s...' %script_path)
                subprocess_args = [script_path,str(self.memory),self.subnet,self.security_group]
                returncode = self.subprocess_popen(subprocess_args)

                if returncode == 0:
                
                    returncode = self.subprocess_popen(subprocess_args)
                    script_path = os.path.join(self.scriptsdir,"pegasus-aws-batch-create.sh")
                    self.logger.info ('Calling %s...' %script_path)
                    subprocess_args = [script_path,self.workingdir,prefix]
                    returncode = self.subprocess_popen(subprocess_args)
    
                    if returncode == 0:
                    
                        self.display_output (f'Planning the workflow for {len(wf.jobs)} workflow jobs...')
                        wf.plan(conf='./pegasusrc',\
                                cluster = ['horizontal'],\
                                sites = ['aws-batch'],\
                                output_sites = ['local'],\
                                dir = './dags',\
                                force = True,\
                                submit = False)
    
                        submit_dir = wf.braindump.submit_dir
                        self.logger.info ('submit_dir: %s' %str(submit_dir))
    
                        if os.path.exists(submit_dir):
                        
                            #'''
                            self.display_output ('Running the workflow, submit_dir: %s...' %str(submit_dir))
                            wf.run()
                            self.logger.info ('wf.run_output: %s\n' %str(wf.run_output))
                        
                            self.display_output ('Waiting for the workflow to complete...')
                            wf.wait()
                            #'''
                            
                            script_path = os.path.join(self.scriptsdir,"pegasus-analyzer.sh")
                            self.logger.info ('Calling %s...' %script_path)
                            subprocess_args = [script_path,self.workflow_results_directory,submit_dir]
                            returncode = self.subprocess_popen(subprocess_args)
                            if returncode != 0:
                                self.logger.warning ('pegasus-analyzer.sh returned nonzero returncode: %s' %str(returncode))
    
                            script_path = os.path.join(self.scriptsdir,"pegasus-statistics.sh")
                            self.logger.info ('Calling %s...' %script_path)
                            subprocess_args = [script_path,self.workflow_results_directory,submit_dir]
                            returncode = self.subprocess_popen(subprocess_args)
                            if returncode != 0:
                                self.logger.warning ('pegasus-statistics.sh returned nonzero returncode: %s' %str(returncode))
    
                            # Clean up
                            
                            self.display_output("Cleanup...")
    
                            script_path = os.path.join(self.scriptsdir,"pegasus-s3-rm.sh")
                            self.logger.info ('Calling %s...' %script_path)
                            subprocess_args = [script_path,S3_URL_PREFIX,S3_BUCKET,S3_BUCKET_KEY]
                            returncode = self.subprocess_popen(subprocess_args)
                            if returncode != 0:
                                self.logger.warning ('pegasus-s3-rm.sh returned nonzero returncode: %s' %str(returncode))
            
                            script_path = os.path.join(self.scriptsdir,"pegasus-aws-batch-delete.sh")
                            self.logger.info ('Calling %s...' %script_path)
                            subprocess_args = [script_path,self.workingdir,prefix]
                            returncode = self.subprocess_popen(subprocess_args)
                            if returncode != 0:
                                self.logger.warning ('pegasus-aws-batch-delete.sh returned nonzero exitCode: %s' %str(exitCode))
    
                            #shutil.rmtree(submit_dir)

                            for i in range(cfg.NUM_LISTS):
 
                                bin_filename = cfg.BIN_LISTS[i][self.template_index]
                                if bin_filename != None:
                                    bin_filepath1 = os.path.join(self.workflow_results_directory, bin_filename)
                                    bin_filepath2 = os.path.join(bin_dir, bin_filename)
                                    if os.path.exists(bin_filepath1):
                                        shutil.move(bin_filepath1, bin_filepath2)
                            return 0
                            
                        else:
                            self.logger.error ('Wrapper.py run_workflow: Pegasus submit directory %s not created' %submit_dir)
                            return 1
                    
                    else:
                        self.logger.error ('Wrapper.py run_workflow: pegasus-aws-batch-create.sh returned nonzero returncode: %s' %str(returncode))
                        return 1
                 
                else:
                    self.logger.error ('Wrapper.py run_workflow: ppegasus-aws-batch-configure.sh returned nonzero returncode: %s' %str(returncode))
                    return 1
                    
            except PegasusClientError as e:
            
                self.logger.error ('launch_wrapper.py run_workflow: PegasusClientError Exception: %s\n' %str(e))
                return 1

        except Exception as e:
            
            self.logger.error ('LaunchWrapper Exception: %s\n' %str(e))
            return 1

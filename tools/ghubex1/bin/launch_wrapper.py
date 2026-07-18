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
        
            print ('LaunchWrapper.run_workflow...')
            
            template =  cfg.TEMPLATE_LIST[self.template_index]
            print ('template: %s' %template)

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
            S3_BUCKET = 'ghub-tools-%s' %bucket_name_suffix
            #print ('S3_BUCKET: ', S3_BUCKET)
            os.environ['S3_BUCKET'] = S3_BUCKET
            self.logger.info("os.environ['S3_BUCKET']: %s" %str(os.environ['S3_BUCKET']))
            # The S3_BUCKET_KEY (i.e. directory) is created for each workflow run and deleted after each workflow run.
            S3_BUCKET_KEY = 'pegasus-workflow'
            #print ('S3_BUCKET_KEY: ', S3_BUCKET_KEY)
            os.environ['S3_BUCKET_KEY'] = S3_BUCKET_KEY
            self.logger.info("os.environ['S3_BUCKET_KEY']: %s" %str(os.environ['S3_BUCKET_KEY']))

            ########################################################################
            # Create and plan the Pegasus WMS workflow
            ########################################################################

            workflow_name = 'ghubex1_%s_launch_workflow_%s' %(template, self.user)
            #print ('workflow_name: ', workflow_name)
            wf = Workflow(workflow_name)
            #print ('wf: ', wf)
    
            ########################################################################
            # Create and configure the Transformation Catalog
            ########################################################################

            tc = TransformationCatalog()
            wf.add_transformation_catalog(tc)
            
            # Add the launch script to the Transformation Catalog. The launch script is run on CCR via SLURM.
             
            tooldir = os.path.dirname(os.path.dirname(os.path.realpath(os.path.abspath(__file__))))
            #print ('tooldir: ', tooldir)
            workingdir = os.getcwd()
            #print ('workingdir: ', workingdir)
            
            launch_exec_path =  os.path.join(workingdir, 'remotebin', template, '%s_Launch.sh' %template)
            print ("launch_exec_path: %s" %launch_exec_path)
            
            launch_exec = Transformation(
                '%sLaunch' %template,
                site='local',
                pfn=launch_exec_path,
                is_stageable = True, #Stageable or installed
                arch=Arch.X86_64,
                os_type=OS.LINUX)
                #os_release="rhel")
            tc.add_transformations(launch_exec)
            
            ########################################################################
            # Create and configure the Replica Catalog
            ########################################################################

            rc = ReplicaCatalog()
            wf.add_replica_catalog(rc)

            # PFNs:

            # All files in a Pegasus workflow are referred to in the DAX using their Logical File Name (LFN).
            # These LFNs are mapped to Physical File Names (PFNs) when Pegasus plans the workflow.
            # Add input files to the DAX-level replica catalog

            # Create the f.a input file for the first workflow job
            
            f_a_filepath = os.path.join(workingdir, 'f.a')
            print ('f_a_filepath: %s' %f_a_filepath)
            fp = open(f_a_filepath,'w')
            if fp:
               fp.write('{0}\n'.format(self.lunch_items.rstrip()))
               fp.close()
            else:
               print ('Could not create the %s input file.\n' %f_a_filepath)
               return 1

            jobs_dir = os.path.join('bin', template)
            job1 = cfg.JOB1_LIST[self.template_index]
            job2 = cfg.JOB2_LIST[self.template_index]
    
            job1filepath = os.path.join(tooldir, jobs_dir, job1)
            print ('job1filepath: %s' %job1filepath)
            rc.add_replica('local', File(job1), job1filepath)
            job2filepath = os.path.join(tooldir, jobs_dir, job2)
            print ('job2filepath: %s' %job2filepath)
            rc.add_replica('local', File(job2), job2filepath)
            rc.add_replica('local', File('f.a'), f_a_filepath)

            ########################################################################
            # Add jobs to the workflow
            ########################################################################

            # On Ghub, .add_outputs register_replica must be set to False (the default is True) to prevent
            # Pegasus from returning with a post script failure.
            
            workflow_job1 = Job(launch_exec)\
                .add_args("""%s %s""" %(job1, self.user))\
                .add_inputs(File(job1))\
                .add_inputs(File('f.a'))\
                .add_outputs(File('f.b'), stage_out=False, register_replica=False)\
                .add_metadata(time='%d' %self.maxwalltime)
            wf.add_jobs(workflow_job1)

            workflow_job2 = Job(launch_exec)\
                .add_args("""%s""" %job2)\
                .add_inputs(File(job2))\
                .add_inputs(File('f.b'))\
                .add_outputs(File('f.c'), stage_out=True, register_replica=False)\
                .add_metadata(time='%d' %self.maxwalltime)
            wf.add_jobs(workflow_job2)
            
            # job2 depends on job1 completing
            
            wf.add_dependency(workflow_job2, parents=[workflow_job1])

            ########################################################################
            # Create the YAML (YAML Ain't Markup Language) file
            ########################################################################

            try:
                wf.write('launch_workflow.yml')
            except PegasusClientError as e:
                print(str(e))
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
                    
                        self.display_output ('Planning the workflow...')
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
                            self.display_output ('Running for the workflow...')
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
    
                            shutil.rmtree(submit_dir)
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
            
                print ('launch_wrapper.py run_workflow: PegasusClientError Exception: %s\n' %str(e))
                return 1

        except Exception as e:
            
            print ('LaunchWrapper Exception: %s\n' %str(e))
            return 1

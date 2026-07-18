# Ghub Pegasus WMS Tutorial and Templates

This Jupyter Notebook tool repository provides an introductory tutorial and templates for running [Pegasus Workflow Management System (WMS)](https://pegasus.isi.edu) workflows for Ghub and provides Pegasus pipeline workflow templates that associates two simple workflow jobs to create a "Hello World" demonstration of Pegasus. 

The repository contains a Dockerfile for JupyterHub DockerSpawner, which enables JupyterHub to provision an individual user notebook server within isolated Docker containers for the tool.

- Templates are  provided for workflow jobs written in the `Bash`, `C`, `CPP`, `Fortran`, `MATLAB`, `Python` and `R` programming languages. Each programming language requires a different template because the scripts to launch the `Bash`, `Python`, and `R` scripts, and the scripts to build and launch the binary executables for the `C`, `CPP`, `Fortran`, and `MATLAB` source codes, are different for each programming language. The templates' scripts and source codes provide a guideline for you to create your Pegasus WMS workflow tool for Ghub.  

- The Pegasus WMS comprises software that automates and manages the execution of computational workflow jobs, including staging the jobs, distributing the work, submitting the jobs for execution, as well as handling data flow dependencies and overcoming job failures. The tool is designed to follow the Pegasus WMS, Amazon AWS Batch deployment scenario, which, in turn, is based on the [Amazon AWS Fetch & Run Example](https://aws.amazon.com/blogs/compute/creating-a-simple-fetch-and-run-aws-batch-job/). See the [Welcome to Pegasus WMS’s documentation! Deployment Scenarios](https://pegasus.isi.edu/documentation/user-guide/deployment-scenarios.html), Amazon AWS Batch section, for more information. 

- The tool runs two Docker images, a remotehostimage Docker image and a submithostimage Docker image. The remotehostimage Docker image is the Fetch & Run Docker image and contains software to run the scripts and build and launch the binary executables for the templates, and, also includes the Bash Fetch & Run script and ENTRYPOINT. The submithostimage Docker image contains the software required to implement the workflow, including a Jupyter Notebook as the interface for running the workflow, HTCondor, and the Pegasus WMS.

## One-Time Amazon AWS Batch Setup

This tool requires that you complete the following prerequisites for configuring Amazon AWS Batch.

- Create an IAM account and an IAM user with administrative access. See [Create IAM account and administrative user](https://docs.aws.amazon.com/batch/latest/userguide/create-an-iam-account.html) for information on how to do this. Create an access key pair for the IAM user. See [Manage access keys for IAM users](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_access-keys.html) for information on how to do this.

- Sign in as the IAM user and create the IAM roles required for Pegasus Amazon AWS Batch. These are an AWS Batch Service IAM Role named AWSBatchServiceRole, an Amazon Elastic Container Service (ECS) Instance Role named ecsInstanceRole, and an IAM Role named batchJobRole. See the Pegasus WMS 
[Deployment Scenarios](https://pegasus.isi.edu/documentation/user-guide/deployment-scenarios.html), Amazon AWS Batch section, for more information.

- Sign in as the IAM user and create a Virtual Private Cloud (VPC) and security group for your Amazon AWS Region. See [Create a VPC](https://docs.aws.amazon.com/batch/latest/userguide/create-a-vpc.html) and [Create a security group](https://docs.aws.amazon.com/batch/latest/userguide/create-a-base-security-group.html) for information on how to do this.

- Install the Amazon AWS CLI on your personal computer. See [Getting started with the AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-getting-started.html) for more information on how to do this.

## Configure Pegasus Amazon AWS Batch

AWS Batch comprises four components for a workflow: a compute environment, a job definition, a job queue, and the jobs. Pegasus Amazon AWS Batch provides an interface for creating and managing these AWS Batch components. To do this, Pegasus requires an AWS credential file, an AWS S3 configuration file, and JSON-formatted information catalogs. These files contain fields that reference your AWS authorization credentials. See the Pegasus WMS [Deployment Scenarios](https://pegasus.isi.edu/documentation/user-guide/deployment-scenarios.html), Amazon AWS Batch section, for more information.

### Configuration Requirements

This tool requires two AWS authorization credentials files: ~/.aws/config and ~/.aws/credentials. 

- Required contents of the ~/.aws/config file:<br/>
[default]<br/>
account_id = *<br />
region = *

- Required contents of the ~/.aws/credentials file:<br/>
[default]<br/>
aws_access_key_id = *<br />
aws_secret_access_key = *

	Where * is replaced with your IAM account and IAM user authorization credentials.

### Configuration Command
	
This tool's ./remosthost and ./submithost directories contain templates for the files that Pegasus requires. The ./pegasus-wms-configure.sh Bash script configures these files with your AWS authorization credentials.

- **Note: source ./pegasus-wms-configure.sh must be executed before building the remotehostimage and submithostimage Docker images.**

## Build the Docker Images

### Build the remotehostimage Docker image and push the image to the Amazon Elastic Cloud Registry (ECR).

- source ./pegasus-wms-configure.sh
- source ./build_remotehostimage_and_push_to_ECR.sh

### Build the submithostimage Docker image

- source ./pegasus-wms-configure.sh<br>
- source ./build_submithostimage.sh ghubex1

## Launch and Run the Workflow

### Launch a Jupyter Notebook stored locally using JupyterHub DockerSpawner

Enter source ./launch_submithostimage.sh ghubex1 to start a JupyterHub and Server and run the tool's Docker image. This runs a single-user JupyterHub and Server using the jupyterhub.auth.DummyAuthenticator for development testing only.

### Login to JupyterHub

When the *JupyterHub is now running at...*  message appears, open a web browser and enter the URL: localhost\:8000, sign in with username: jovyan, password is not required. DockerSpawner will take the authenicated user and spin up an individual, isolated single-user notebook server inside a Docker container. Open the tool's ghubex1.ipynb Jupyter notebook and select Restart Kernel and Run All Cells.

Follow the processing steps in ghubex1.ipynb to launch and run the workflow.

### Logout of JupyterHub
   
Logout of the Jupyter notebook.

Enter Control-C to stop the JupyterHub and Server.

Enter source ./remove_tool.sh <tool_alias_name> to remove any containers, volumes and images created for the tool.

### Workflow Results

- Results and interim files generated for running a workflow are stored in the mounted ./submithost//LOCAL/shared-storage directory.



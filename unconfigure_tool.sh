#!/bin/bash

rm -f ./submithost/build.log
rm -f ./remotehost/build.log
rm -f ./anaconda/Miniconda3-py310_25.11.1-1-Linux-x86_64.sh

cp -f ./submithost/pegasusrc_template ./submithost/pegasusrc
cp -f ./submithost/amazon-aws-credentials/.aws/aws_config_template ./submithost/amazon-aws-credentials/.aws/config
cp -f ./submithost/amazon-aws-credentials/.aws/aws_credentials_template ./submithost/amazon-aws-credentials/.aws/credentials
cp -f ./submithost/amazon-aws-credentials/.pegasus/pegasus_credentials_conf_template ./submithost/amazon-aws-credentials/.pegasus/credentials.conf
cp -f ./submithost/pegasus-wms-configuration-files/job_definition_json_template ./submithost/pegasus-wms-configuration-files/job-definition.json
cp -f ./submithost/pegasus-wms-configuration-files/compute_env_json_template ./submithost/pegasus-wms-configuration-files/compute-env.json
cp -f ./remotehost/push-remotehostimage-to-ECR_sh_template ./remotehost/push-remotehostimage-to-ECR.sh

if [ -d "./submithost/LOCAL/shared-storage" ] && [ -n "$(ls -A ./submithost/LOCAL/shared-storage)" ]; then
    rm -rf ./submithost/LOCAL/shared-storage/*
    rm -rf ./submithost/LOCAL/shared-storage/.ipynb_checkpoints
fi

:

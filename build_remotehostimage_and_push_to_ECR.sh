#!/bin/bash -l
tool_alias_name=$1
echo "building remotehost image for "${tool_alias_name}"..."

[ -n "$(docker images -q remotehostimage)" ] && docker rmi remotehostimage
docker image build -f ./remotehost/Dockerfile -t remotehostimage . 2>&1 | tee build.log && source ./remotehost/push-remotehostimage-to-ECR.sh

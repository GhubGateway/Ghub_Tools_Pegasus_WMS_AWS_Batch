#!/bin/bash -l
tool_alias_name=$1
echo "launching "${tool_alias_name}"..."

source ./remove_jupyterhub.sh

(cd ./submithost && docker compose build --no-cache && docker compose up)

# While the Hub is running, verify the Hub's password by entering the following in a terminal window:
#docker exec jupyterhub printenv HUB_USER_PASSWORD

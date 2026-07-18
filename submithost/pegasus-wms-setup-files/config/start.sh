#!/bin/bash

# set up the jupyter notebook
# if [ "x$NOTEBOOK_PASSWORD" = "x" ]; then
#     NOTEBOOK_PASSWORD="emulator"
# fi
# if [ "x$NOTEBOOK_BASE_URL" = "x" ]; then
#     NOTEBOOK_BASE_URL="/"
# fi
# ENCPASSWORD=$(python3 -c "from jupyter_server.auth importpasswd;print(passwd(\"$NOTEBOOK_PASSWORD\"))")
#mkdir -p /home/jovyan/.jupyter
# cat >/home/jovyan/.jupyter/jupyter_server_config.json <<EOF
# { "ServerApp":
#    { 
#       "base_url": "$NOTEBOOK_BASE_URL",
#       "password": "$ENCPASSWORD"
#    }
# }
# EOF
#chown -R jovyan: /home/jovyan/.jupyter
# cat /home/jovyan/.jupyter/jupyter_server_config.json

exec /usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf


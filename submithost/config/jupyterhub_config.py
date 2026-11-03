
# Main configuration file for JupyterHub
# References:
#     https://oneuptime.com/blog/post/2026-02-08-how-to-set-up-jupyterhub-in-docker-for-teams/view
#     Anthropic Claude

import os

# --- Spawner Configuration ---
# Use DockerSpawner to create a container for each user.
# DockerSpawner is a specific implementation that inherits from the abstract Spawner class
c.JupyterHub.spawner_class = 'dockerspawner.DockerSpawner'

# The Docker image each user gets
c.DockerSpawner.image =  'ghubex1_tool_image:latest'
# Prevent Docker from trying to pull the image from a registry
c.DockerSpawner.pull_policy = 'Never' 

# Connect containers to the JupyterHub network
c.DockerSpawner.network_name = 'jupyterhub-network'

# Docker Desktop (macOS) exposes the host's ssh-agent at this magic path.
# Inside the container it appears owned by root, so jovyan cannot open it
# ("Error connecting to agent: Permission denied"). The ssh-agent-relay
# program in supervisord.conf (runs as root) re-publishes it as
# /home/jovyan/.ssh/agent.sock, owned by jovyan, mode 0600.
AGENT_SOCK = "/run/host-services/ssh-auth.sock"          # host side (Docker Desktop)
AGENT_RELAY_SOCK = "/home/jovyan/.ssh/agent.sock"        # what jovyan uses
AGENT_OWNER = os.environ.get("HUB_AGENT_OWNER", "")     # set in docker-compose.yml

def pre_spawn_hook(spawner):
    if spawner.user.name == AGENT_OWNER:
        # copy, don't mutate, the shared config dicts
        spawner.volumes = {**spawner.volumes, AGENT_SOCK: {"bind": AGENT_SOCK, "mode": "rw"}}
        spawner.environment = {**spawner.environment, "SSH_AUTH_SOCK": AGENT_RELAY_SOCK}

c.DockerSpawner.pre_spawn_hook = pre_spawn_hook

# Mount a persistent volume for each user's work
notebook_dir = '/home/{username}/ghubex1'
c.DockerSpawner.notebook_dir = notebook_dir
c.DockerSpawner.volumes = {
    'jupyterhub-user-{username}': notebook_dir,
    f'%s' %os.path.join(os.environ.get("HOST_DEPLOY_DIR"), "LOCAL", "shared-storage"): {"bind": "/home/{username}/ghubex1/LOCAL/shared-storage", "mode": "rw"}
}

# Default is /tree/ for jupyterlab
# Appmode (https://github.com/oschuett/appmode):
#c.DockerSpawner.args = ['--ServerApp.default_url=/apps/ghubex1.ipynb']
# Edit mode: 
#c.DockerSpawner.args = ['--ServerApp.default_url=/notebooks/ghubex1.ipynb']

# Remove containers when users stop their servers
c.DockerSpawner.remove = True

# Set resource limits per user
#c.DockerSpawner.mem_limit = '2G'
#c.DockerSpawner.cpu_limit = 1.0

# --- Hub Configuration ---
# The Hub must be accessible from the spawned containers
#c.JupyterHub.hub_ip = '127.0.0.1'
c.JupyterHub.hub_connect_ip = 'jupyterhub'

# --- Authentication ---
# DummyAuthenticator accepts ANY username and ANY password. Because a hub
# login gives a terminal that can use your Vortex ssh key through the agent,
# never use it once the agent is mounted.
#c.JupyterHub.authenticator_class = 'jupyterhub.auth.DummyAuthenticator'

# Minimum for a single-user hub on your own PC (JupyterHub >= 5.1):
# one shared password, one allowed username, hub reachable only from
# 127.0.0.1 (see ports: in docker-compose.yml).
c.JupyterHub.authenticator_class = 'shared-password'
c.SharedPasswordAuthenticator.user_password = os.environ["HUB_USER_PASSWORD"]  # >= 8 chars, set in .env
c.Authenticator.allowed_users = {os.environ.get("HUB_AGENT_OWNER", "jovyan")}
c.Authenticator.allow_all = False
# Use native authenticator for simple username/password auth
#c.JupyterHub.authenticator_class = 'nativeauthenticator.NativeAuthenticator'
#c.NativeAuthenticator.minimum_password_length = 8
#c.NativeAuthenticator.open_signup = False

# Admin users who can manage the hub. None needed for a single-user hub;
# with DummyAuthenticator, 'admin' could be claimed by anyone.
#c.Authenticator.admin_users = {'admin'}

# --- Proxy Configuration ---
c.ConfigurableHTTPProxy.should_start = True

# --- Misc Settings ---
c.JupyterHub.cleanup_servers = True
c.JupyterHub.shutdown_on_logout = False

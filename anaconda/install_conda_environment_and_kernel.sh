#!/bin/bash -l

# Create the associated kernel for environment.
#
# Usage:
# source ./k.sh environment

environment=$1
echo "environment: "$environment

conda=$(which conda)
echo "conda: "${conda}
#echo "#conda: "${#conda}
# Length of /bin/conda = 10
len=$(( ${#conda} - 10 ))
#echo "len: "${len}
conda_root=${conda:0:len}
echo "conda_root: "${conda_root}

conda config --add channels conda-forge
conda config --set channel_priority strict

tool_env_dir=${conda_root}/envs/${environment}
tool_kernel_json_dir="${conda_root}/share/jupyter/kernels/${environment}"

echo "Creating the env "${environment}"..."
conda create -c conda-forge --name ${environment} "python=3.10" -y  
echo "Env ${environment} created"
conda env list

. /home/anaconda/anaconda-7/bin/activate ${environment}
echo "Env ${environment} activated"

which python
conda install -c conda-forge gitpython htcondor htcondor-cli ipywidgets ipykernel jupyter jupyterhub notebook numpy openjdk pegasus-wms python-htcondor python-pegasus-wms -y
python -m pip install hublib==0.9.97
conda list

python -c "import Pegasus.api; print('Pegasus API is ready')"

echo "Installing the kernel for env "${environment}"..."

python -m ipykernel install --sys-prefix --name ${environment} --display-name "Python3 (${environment})"
python -m ipykernel install --prefix ${conda_root} --name ${environment} --display-name "Python3 (${environment})"

KERNEL_JSON_PATH="${tool_kernel_json_dir}/kernel.json"
# For the environment to get activated when the kernel is selected, modify ${KERNEL_JSON_PATH} and add the PATH env variable. For a reference see /apps/share64/debian10/anaconda/anaconda-7/share/jupyter/kernels/geospatial-2021-09/kernel.json.
echo ${KERNEL_JSON_PATH}

# Define the environment variable name and value
ENV_VAR_NAME="PATH"
#echo ${ENV_VAR_NAME}
ENV_VAR_VALUE="${tool_env_dir}/bin:${conda_root}/bin:/bin:/usr/bin:/usr/bin/X11:/sbin:/usr/sbin"
#echo ${ENV_VAR_VALUE}

# Check if the kernel.json file exists
if [ ! -f "${KERNEL_JSON_PATH}" ]; then
    echo "Error: kernel.json not found at ${KERNEL_JSON_PATH}"
else
    # jq is like sed for JavaScript Object Notation (JSON) data.
    # Add or update the environment variable in the 'env' section of kernel.json
    # If 'env' does not exist, it will be created.
    # If the variable already exists, its value will be updated.
    jq --arg name "$ENV_VAR_NAME" --arg value "$ENV_VAR_VALUE" \
       '.env += {($name): $value}' "${KERNEL_JSON_PATH}" > "${KERNEL_JSON_PATH}.tmp" && \
    mv "${KERNEL_JSON_PATH}.tmp" "${KERNEL_JSON_PATH}"

    #echo "Environment variable '${ENV_VAR_NAME}' added/updated in ${KERNEL_JSON_PATH}"
    
    #echo "${KERNEL_JSON_PATH}:"
    cat ${KERNEL_JSON_PATH}
fi

. /home/anaconda/anaconda-7/bin/deactivate
echo "Env ${environment} deactivated"


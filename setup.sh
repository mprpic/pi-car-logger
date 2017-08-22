#!/bin/bash

declare -a deps=("python-gps" "python-virtualenv")
declare -a missing_deps=()

for app in "${deps[@]}"; do
    installed=$(dpkg -l "${app}" 2>/dev/null | egrep '^ii' | wc -l) 
    if [ $installed -eq 0 ]; then
        missing_deps+=("${app}")
    fi
done

if ! grep -q "start_x=1" /boot/config.txt; then
    echo 'WARNING: Camera module not enabled; run raspi-config to enable it'
fi

if [ -z "$missing_deps" ]; then
    # Set up a virtual environment (including system packages since
    # python-gps is not available in PyPI)
    /usr/bin/virtualenv --system-site-packages venv

    # Install requirements
    venv/bin/pip install -r requirements.txt

else
    echo -e "ERROR: Missing dependencies, please install with:\n"
    echo -n "sudo apt-get install "
    echo "${missing_deps[@]}"
fi

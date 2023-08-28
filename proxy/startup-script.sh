#!/bin/bash

echo -e 'admin\tALL=(ALL)\tNOPASSWD: ALL' >> /etc/sudoers

source /etc/os-release

# All Fedora GCP images do not support auto resize root disk
# In Fedora rawhide(39), python3-dnf is not installed in image
if [[ "$ID" == "fedora" ]]; then
    growpart /dev/sda 5
    btrfs filesystem resize 1:+70G /
    dnf install -y python3 python3-dnf
fi

# Enable CRB repo or powertools repo on Centos Stream 9 or 8
if [[ "${ID}-${VERSION_ID}" == "centos-9" ]]; then
    dnf config-manager --set-enabled crb
fi
if [[ "${ID}-${VERSION_ID}" == "centos-8" ]]; then
    dnf config-manager --set-enabled powertools
fi

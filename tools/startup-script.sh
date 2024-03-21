#!/bin/bash

echo -e 'admin\tALL=(ALL)\tNOPASSWD: ALL' >> /etc/sudoers

source /etc/os-release

# All Fedora GCP images do not support auto resize root disk
if [[ "$ID" == "fedora" ]]; then
    if [[ "$VERSION_ID" == "40" || "$VERSION_ID" == "41"  ]]; then
        growpart /dev/sda 4
    else
        growpart /dev/sda 5
    fi
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

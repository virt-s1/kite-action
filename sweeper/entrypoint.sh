#!/bin/bash

if ! whoami &> /dev/null; then
  if [ -w /etc/passwd ]; then
    echo "sweeper:x:$(id -u):$(id -g):,,,:${HOME}:/bin/bash" >> /etc/passwd
    echo "sweeper:x:$(id -G | cut -d' ' -f 2)" >> /etc/group
  fi
fi

TOKEN=$(cat "/var/run/secrets/kubernetes.io/serviceaccount/token")
oc login https://paas.psi.redhat.com:443 --token=${TOKEN}
oc project virt-qe-3rd

exec "$@"

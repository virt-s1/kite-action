#!/bin/bash

if ! whoami &> /dev/null; then
  if [ -w /etc/passwd ]; then
    echo "proxy:x:$(id -u):$(id -g):,,,:${HOME}:/bin/bash" >> /etc/passwd
    echo "proxy:x:$(id -G | cut -d' ' -f 2)" >> /etc/group
  fi
fi

exec "$@"

### Proxy server for kite project on OpenShift
FROM quay.io/fedora/fedora:36-x86_64

LABEL name="kite-proxy" \
      maintainer="xiaofwan@redhat.com" \
      vendor="Red Hat QE Section 1" \
      version="2" \
      release="1" \
      summary="kite proxy server" \
      description="A proxy server to fetch AWS SQS message repeatly" \
      io.k8s.description="A proxy server to fetch AWS SQS message repeatly" \
      io.k8s.display-name="kite proxy" \
      io.openshift.tags="kite-proxy,kite,proxy"

ENV PROXY_ROOT=/home/proxy

USER root

ADD https://password.corp.redhat.com/RH-IT-Root-CA.crt \
    /etc/pki/ca-trust/source/anchors/
RUN update-ca-trust extract

# Google Cloud SDK repo
COPY google-cloud-sdk.repo /etc/yum.repos.d/

RUN mkdir -p ${PROXY_ROOT}
COPY proxy.py entrypoint.sh install_runner.yaml delete_os_instance.yaml startup-script.sh /home/proxy
COPY key /home/proxy/key/
COPY ansible.cfg /etc/ansible/

RUN dnf -y update && \
    dnf -y install \
        ansible-core \
        curl \
        gcc \
        google-cloud-cli \
        net-tools \
        procps-ng \
        python3 \
        python3-devel \
        python3-pip && \
    dnf clean all && \
    pip install boto3 botocore openstacksdk==0.61.0 && \
    ansible-galaxy collection install -p ${PROXY_ROOT}/.ansible/collections openstack.cloud community.general && \
    chmod -R g=u ${PROXY_ROOT} /etc/passwd /etc/group && \
    chgrp -R 0 ${PROXY_ROOT} && \
    chmod 755 ${PROXY_ROOT}/{proxy.py,entrypoint.sh,startup-script.sh}

WORKDIR ${PROXY_ROOT}

USER 1001

ENTRYPOINT ["/home/proxy/entrypoint.sh"]
CMD ["python3", "-u","/home/proxy/proxy.py"]

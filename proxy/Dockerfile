### Proxy server for kite project on OpenShift
FROM quay.io/fedora/fedora:36-x86_64

LABEL name="kite-proxy" \
      maintainer="xiaofwan@redhat.com" \
      vendor="Red Hat QE Section 1" \
      version="2.0" \
      release="1" \
      summary="kite proxy server" \
      description="A proxy server to fetch AWS SQS message repeatly" \
      io.k8s.description="A proxy server to fetch AWS SQS message repeatly" \
      io.k8s.display-name="kite proxy" \
      io.openshift.tags="kite-proxy,kite,proxy"

ENV PROXY_ROOT=/home/proxy

USER root

# install red hat root CA to access red hat internal https service
ADD https://password.corp.redhat.com/RH-IT-Root-CA.crt \
    /etc/pki/ca-trust/source/anchors/
RUN update-ca-trust extract

RUN dnf -y update && \
    dnf -y install \
        net-tools \
        procps-ng \
        curl \
        gcc \
        python3 \
        python3-devel \
        python3-pip && \
    dnf clean all && \
    pip install boto3 requests && \
    mkdir -p ${PROXY_ROOT} && \
    chmod -R g=u ${PROXY_ROOT} /etc/passwd /etc/group && \
    chgrp -R 0 ${PROXY_ROOT}

COPY proxy.py entrypoint.sh /home/proxy/
RUN chmod 755 ${PROXY_ROOT}/{proxy.py,entrypoint.sh}

WORKDIR ${PROXY_ROOT}

USER 1001

ENTRYPOINT ["/home/proxy/entrypoint.sh"]
CMD ["python3", "-u","/home/proxy/proxy.py"]

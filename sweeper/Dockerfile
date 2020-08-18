### Sweep un-used github action runner
FROM fedora:32

LABEL name="kite-sweeper" \
      maintainer="xiaofwan@redhat.com" \
      vendor="Red Hat QE Section 1" \
      version="1.0" \
      release="1" \
      summary="Remove un-used github action runner" \
      description="Clean un-used github action runner every day" \
      io.k8s.description="Clean un-used github action runner every day" \
      io.k8s.display-name="runner sweeper" \
      io.openshift.tags="kite-sweeper,sweeper,kite"

ENV SWEEPER_ROOT=/home/sweeper
ENV KUBECONFIG=${SWEEPER_ROOT}/.kube/config

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
        libev-devel \
        python3 \
        python3-devel \
        python3-pip && \
    dnf clean all && \
    pip install requests pyyaml && \
    curl -o /usr/bin/oc http://file-server-virt-qe-3rd.cloud.paas.psi.redhat.com/oc && \
    chmod 755 /usr/bin/oc && \
    mkdir -p ${SWEEPER_ROOT} && \
    chmod -R g=u ${SWEEPER_ROOT} /etc/passwd /etc/group && \
    chgrp -R 0 ${SWEEPER_ROOT}

COPY sweeper.py entrypoint.sh /home/sweeper/
RUN chmod 755 ${SWEEPER_ROOT}/{sweeper.py,entrypoint.sh}

WORKDIR ${SWEEPER_ROOT}

USER 1001

ENTRYPOINT ["/home/sweeper/entrypoint.sh"]
CMD ["python3", "-u", "/home/sweeper/sweeper.py"]

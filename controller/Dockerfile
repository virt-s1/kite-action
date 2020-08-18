### Github action controller on OpenShift
FROM fedora:32

LABEL name="kite-controller" \
      maintainer="xiaofwan@redhat.com" \
      vendor="Red Hat QE Section 1" \
      version="1.0" \
      release="1" \
      summary="Github self-host action controller" \
      description="Github action controller for kite project on OpenShift" \
      io.k8s.description="Github action controller for kite project on OpenShift" \
      io.k8s.display-name="kite controller" \
      io.openshift.tags="kite-controller,github-action-controller"

ENV CONTROLLER_ROOT=/home/controller
ENV KUBECONFIG=${CONTROLLER_ROOT}/.kube/config

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
    pip install bottle requests bjoern pyyaml && \
    curl -o /usr/bin/oc http://file-server-virt-qe-3rd.cloud.paas.psi.redhat.com/oc && \
    chmod 755 /usr/bin/oc && \
    mkdir -p ${CONTROLLER_ROOT} && \
    chmod -R g=u ${CONTROLLER_ROOT} /etc/passwd /etc/group && \
    chgrp -R 0 ${CONTROLLER_ROOT}

COPY controller.py entrypoint.sh /home/controller/
RUN chmod 755 ${CONTROLLER_ROOT}/{controller.py,entrypoint.sh}

EXPOSE 8080

WORKDIR ${CONTROLLER_ROOT}

USER 1001

ENTRYPOINT ["/home/controller/entrypoint.sh"]
CMD ["/home/controller/controller.py"]

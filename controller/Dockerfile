### Github action controller on OpenShift
FROM fedora:32

LABEL name="kite-action-controller" \
      maintainer="xiaofwan@redhat.com" \
      vendor="Red Hat QE Section 1" \
      version="1.0" \
      release="1" \
      summary="Github self-host action controller" \
      description="Github action controller for kite project on OpenShift" \
      io.k8s.description="Github action controller for kite project on OpenShift" \
      io.k8s.display-name="kite action controller" \
      io.openshift.tags="kite,github-action,controller"

USER root

RUN dnf -y update && \
    dnf -y install \
        curl \
        gcc \
        libev-devel \
        python3 \
        python3-devel \
        python3-pip && \
    dnf clean all && \
    pip install bottle requests bjoern && \
    curl -k -o /usr/bin/oc https://file-server-virt-qe-3rd.cloud.paas.psi.redhat.com/oc && \
    chmod 755 /usr/bin/oc

COPY controller.py /
RUN chmod 755 /controller.py

EXPOSE 8080

USER 1001
CMD ["/controller.py"]

### dummy Github action runner
# create pod and register as runner
# delete pod to keep runner registed and make it offline
# all test tasks will not fail due to dummy runner
FROM fedora:32

LABEL name="kite-dummy" \
      maintainer="xiaofwan@redhat.com" \
      vendor="Red Hat QE Section 1" \
      version="1.0" \
      release="1" \
      summary="A dummy Github action runner" \
      description="dummy runner means an offline Github action runner" \
      io.k8s.description="dummy runner means an offline Github action runner" \
      io.k8s.display-name="kite dummy runner" \
      io.openshift.tags="kite-dummy,dummy-runner,dummy,kite"

ENV DUMMY_ROOT=/home/dummy
ENV KUBECONFIG=${DUMMY_ROOT}/.kube/config

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
    curl -o /usr/bin/oc https://file-server-virt-qe-3rd.cloud.paas.psi.redhat.com/oc && \
    chmod 755 /usr/bin/oc && \
    mkdir -p ${DUMMY_ROOT} && \
    chmod -R g=u ${DUMMY_ROOT} /etc/passwd /etc/group && \
    chgrp -R 0 ${DUMMY_ROOT}

COPY dummy.py entrypoint.sh /home/dummy/
RUN chmod 755 ${DUMMY_ROOT}/{dummy.py,entrypoint.sh}

WORKDIR ${DUMMY_ROOT}

USER 1001

ENTRYPOINT ["/home/dummy/entrypoint.sh"]
CMD ["python3", "-u", "/home/dummy/dummy.py"]

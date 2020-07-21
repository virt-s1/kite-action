### Github action runner on OpenShift
FROM fedora:32

ARG GH_RUNNER_VERSION

ENV RUNNER_NAME=""
ENV RUNNER_WORK_DIRECTORY="_work"
ENV RUNNER_TOKEN=""
ENV RUNNER_ORGANIZATION_URL=""
ENV RUNNER_LABELS=""
ENV RUNNER_ALLOW_RUNASROOT=true
ENV GITHUB_ACCESS_TOKEN=""

ENV RUNNER_ROOT=/home/runner
ENV PATH=${RUNNER_ROOT}/bin:${PATH} HOME=${RUNNER_ROOT}

LABEL name="kite-action-runner" \
      maintainer="xiaofwan@redhat.com" \
      vendor="Red Hat QE Section 1" \
      version="1.0" \
      release="1" \
      summary="Github self-host action runner" \
      description="Github action runner for kite project on OpenShift" \
      io.k8s.description="Github action runner for kite project on OpenShift" \
      io.k8s.display-name="kite action runner" \
      io.openshift.tags="kite,github-action,runner"

USER root

### Install redhat certs used to access internal https resource
ADD https://password.corp.redhat.com/RH-IT-Root-CA.crt \
    /etc/pki/ca-trust/source/anchors/
RUN update-ca-trust extract

RUN dnf -y update && \
    dnf -y install \
        ansible \
        curl \
        gcc \
        git \
        jq \
        openssl \
        python3 \
        python3-devel \
        python3-pip \
        sed \
        sudo \
        supervisor \
        tar \
        wget \
        zip && \
    dnf clean all && \
    pip install pyvmomi boto boto3 openstacksdk && \
    mkdir -p ${RUNNER_ROOT} && \
    chmod -R g=u ${RUNNER_ROOT} /etc/passwd /etc/group && \
    chgrp -R 0 ${RUNNER_ROOT} && \
    echo "%sudo ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

### The GitHub runner will update itself when receiving a job, if a new release is available.
### In order to allow the runner to exit and restart by itself, the binary is started by a supervisord process.
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf
RUN chmod 644 /etc/supervisor/conf.d/supervisord.conf

WORKDIR ${RUNNER_ROOT}

RUN GH_RUNNER_VERSION=${GH_RUNNER_VERSION:-$(curl --silent "https://api.github.com/repos/actions/runner/releases/latest" | jq -r ".tag_name" | sed 's/^v//')} && \
    curl -L -O https://github.com/actions/runner/releases/download/v${GH_RUNNER_VERSION}/actions-runner-linux-x64-${GH_RUNNER_VERSION}.tar.gz && \
    tar -zxf actions-runner-linux-x64-${GH_RUNNER_VERSION}.tar.gz && \
    rm -f actions-runner-linux-x64-${GH_RUNNER_VERSION}.tar.gz && \
    ./bin/installdependencies.sh && \
    rm -rf /tmp/*

COPY entrypoint.sh /entrypoint.sh
RUN chmod a+rx /entrypoint.sh

USER 1001

ENTRYPOINT ["/entrypoint.sh"]
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]

### Github action runner on OpenShift
FROM fedora:32

ENV RUNNER_NAME=""
ENV RUNNER_WORK_DIRECTORY="_work"
ENV RUNNER_TOKEN=""
ENV RUNNER_ORGANIZATION_URL=""
ENV RUNNER_LABELS=""
ENV RUNNER_ALLOW_RUNASROOT=true
ENV GIT_SSL_NO_VERIFY="true"

ENV RUNNER_ROOT=/home/runner
ENV PATH=${RUNNER_ROOT}/bin:${PATH} HOME=${RUNNER_ROOT}

ARG GITHUB_ACCESS_TOKEN

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

### Install redhat crets used by rcm repo
ADD https://password.corp.redhat.com/RH-IT-Root-CA.crt \
    /etc/pki/ca-trust/source/anchors/
RUN update-ca-trust extract

RUN dnf -y update && \
    dnf -y install \
        ansible \
        curl \
        expect \
        gcc \
        gcc-c++ \
        genisoimage \
        git \
        gnupg \
        jq \
        make \
        openssl \
        python3 \
        python3-devel \
        python3-pip \
        sed \
        sudo \
        supervisor \
        tar \
        unzip \
        wget \
        zip && \
    dnf clean all && \
    pip install flake8 pyvmomi boto boto3 openstacksdk && \
    curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" && \
    unzip awscliv2.zip && \
    ./aws/install && \
    rm -rf aws awscliv2.zip && \
    mkdir -p ${RUNNER_ROOT}

### The GitHub runner will update itself when receiving a job, if a new release is available.
### In order to allow the runner to exit and restart by itself, the binary is started by a supervisord process.
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf
RUN chmod 644 /etc/supervisor/conf.d/supervisord.conf

WORKDIR ${RUNNER_ROOT}

### Get action-runner download URL with actions API
### That requires GITHUB ACCESS TOKEN argument provided when building image
RUN DOWNLOAD_URL=$(curl -fsSL -H "Authorization: token ${GITHUB_ACCESS_TOKEN}" -H "Accept: application/vnd.github.v3+json" https://api.github.com/orgs/virt-s1/actions/runners/downloads | jq -c -r 'map(select(.os == "linux" and .architecture == "x64") | .download_url) | .[]') && \
    curl -L -O ${DOWNLOAD_URL} && \
    tar -zxf actions-runner-linux-x64*.tar.gz && \
    rm -f actions-runner-linux-x64*.tar.gz && \
    ./bin/installdependencies.sh && \
    rm -rf /tmp/* && \
    chmod -R g=u ${RUNNER_ROOT} /etc/passwd /etc/group && \
    chgrp -R 0 ${RUNNER_ROOT}

COPY entrypoint.sh /entrypoint.sh
RUN chmod a+rx /entrypoint.sh

USER 1001

ENTRYPOINT ["/entrypoint.sh"]
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]

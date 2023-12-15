FROM registry.redhat.io/ubi9/ubi-minimal:latest

RUN microdnf install -y python pip git findutils jq \
&& pip install git+https://github.com/openshift-eng/ocp-build-data-validator \
&& pip cache purge \
&& curl -fLo /etc/pki/ca-trust/source/anchors/2022-IT-Root-CA.pem https://certs.corp.redhat.com/certs/2022-IT-Root-CA.pem \
&& curl -fLo /etc/pki/ca-trust/source/anchors/2015-IT-Root-CA.pem https://certs.corp.redhat.com/certs/2015-IT-Root-CA.pem \
&& update-ca-trust extract

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

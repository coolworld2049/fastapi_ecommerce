FROM python:3.11

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
      postgresql-contrib \
      netcat \
      nmap \
      net-tools \
    && apt-get clean \
    && rm -Rf /var/lib/apt/lists/* \
    && rm -Rf /usr/share/doc && rm -Rf /usr/share/man

CMD ["/bin/bash"]
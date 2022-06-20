# (1) enable venv and install dependencies
FROM python:3.9-slim-bullseye AS base

# needed for pip package 'backports.zoneinfo'
RUN apt-get update && apt-get install -y gcc

ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

COPY requirements_linux.txt ./requirements_linux.txt

RUN pip install --upgrade pip wheel
RUN pip install -r requirements_linux.txt

# (2) setup runner image
FROM python:3.9-slim-bullseye AS runner
ENV VIRTUAL_ENV=/opt/venv
WORKDIR /analysis/

COPY --from=base $VIRTUAL_ENV $VIRTUAL_ENV
ENV PATH="/opt/venv/bin:$PATH"

COPY src/ ./src/

RUN ls -a
RUN ls -a src/

# check for running venv
RUN which python
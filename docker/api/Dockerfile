FROM osgeo/gdal:ubuntu-small-3.2.0

RUN apt-get update && apt-get install -y \
    git \
    python3-pip \
    libgeos-3.8.0 \
    libgeos-dev \
    libcairo2 \
    libcairo-gobject2 \
    libpango1.0

# Install fonts for both South Atlantic and Southeast apps
# South Atlantic: Montserrat & Lora
# Southeast: Raleway & Source Sans Pro
RUN mkdir /usr/share/fonts/google && \
    curl https://fonts.google.com/download?family=Montserrat --output /tmp/Montserrat.zip && \
    unzip -o /tmp/Montserrat.zip -d /usr/share/fonts/google && \
    curl https://fonts.google.com/download?family=Lora --output /tmp/Lora.zip && \
    unzip -o /tmp/Lora.zip -d /usr/share/fonts/google && \
    curl https://fonts.google.com/download?family=Raleway --output /tmp/Raleway.zip && \
    unzip -o /tmp/Raleway.zip -d /usr/share/fonts/google && \
    mv /usr/share/fonts/google/static/* /usr/share/fonts/google/ && \
    curl https://fonts.google.com/download?family=Source+Sans+Pro --output /tmp/SourceSansPro.zip && \
    unzip -o /tmp/SourceSansPro.zip -d /usr/share/fonts/google && \
    fc-cache -fv

RUN useradd --create-home app
WORKDIR /home/app
# Note: we are not able to use a user here because we have to mount a volume
# for sharing between containers, which can only be done as root.

ENV PYTHONPATH="${PYTHONPATH}:/home/app"
ENV PYTHONUNBUFFERED 1

# Setup Python dependencies used by API and background worker
# NOTE: these are the same between South Atlantic and Southeast
COPY ./requirements.txt /tmp/requirements.txt
RUN pip3 install --no-warn-script-location -r /tmp/requirements.txt

# Build & install pyogrio (note: update commit SHA1 as required in .env file)
# PYOGRIO_COMMIT_HASH must be provided via --build-arg for docker build
ARG PYOGRIO_COMMIT_HASH
RUN git clone https://github.com/brendan-ward/pyogrio.git /home/app/src/pyogrio && \
    cd /home/app/src/pyogrio && \
    git checkout ${PYOGRIO_COMMIT_HASH} && \
    python setup.py build_ext && \
    python setup.py install && \
    cd /home/app

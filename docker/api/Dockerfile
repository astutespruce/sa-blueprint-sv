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
    unzip /tmp/Montserrat.zip -d /usr/share/fonts/google && \
    curl https://fonts.google.com/download?family=Lora --output /tmp/Lora.zip && \
    unzip -o /tmp/Lora.zip -d /usr/share/fonts/google && \
    curl https://fonts.google.com/download?family=Raleway --output /tmp/Raleway.zip && \
    unzip /tmp/Raleway.zip -d /usr/share/fonts/google && \
    mv /usr/share/fonts/google/static/* /usr/share/fonts/google/ && \
    curl https://fonts.google.com/download?family=Source+Sans+Pro --output /tmp/SourceSansPro.zip && \
    unzip -o /tmp/SourceSansPro.zip -d /usr/share/fonts/google && \
    fc-cache -fv

RUN useradd --create-home app
WORKDIR /home/app
ENV PYTHONPATH="${PYTHONPATH}:/home/app"
ENV PYTHONUNBUFFERED 1

# Build & install pyogrio (note: update commit SHA1 as required)
RUN pip3 install -e git+https://github.com/brendan-ward/pyogrio.git@9bcf43ff7905a1746628f3ff52cacdacb1d1ebfb#egg=pyogrio && \
    cd /home/app/src/pyogrio && \
    python setup.py build_ext && \
    python setup.py install && \
    cd /home/app

COPY ./requirements.txt /tmp/requirements.txt

RUN pip3 install -r /tmp/requirements.txt

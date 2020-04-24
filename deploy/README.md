# Install directly on Ubuntu 18.04

Install deps

```
sudo apt-get update && sudo apt-get install -y curl g++ git unzip libcairo2 libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf2.0-0 libffi-dev \
  libcairo2-dev libgles2-mesa-dev libgbm-dev libllvm3.9 libprotobuf-dev libxxf86vm-dev xvfb x11-utils
```

Note: the deps on line 2 are for mbgl-renderer.

Allocate 2 GB SWAP (more on larger volume):

```
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

Add this to `/etc/fstab`: `/swapfile none swap sw 0 0`

### Workspace

Everything happens in the `~/app` workspace:

```
mkdir ~/app
cd ~/app
```

Generate an SSH keypair, and add a deploy key to the repository per [instructions](https://developer.github.com/v3/guides/managing-deploy-keys/).

Clone `sa-reports` into `~/app/sa-reports`.

### Install nodejs 10

```
cd ~
curl -sL https://deb.nodesource.com/setup_10.x -o nodesource_setup.sh
sudo chmod 777 nodesource_setup.sh && sudo ./nodesource_setup.sh
sudo apt-get install -y nodejs
```

Install mbgl-renderer
Note: runs into permissions issues installing globally

```
npm install mbgl-renderer
```

Test that it starts up

```
node_modules/.bin/mbgl-server
```

### UI

Install gatsby:

```
npm install -g gatsby-cli
```

Build the UI

```
cd ~/app/sa-reports/ui
npm ci
gatsby build
```

## Install python

```
sudo apt install -y software-properties-common
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt install -y python3.8 python3-pip
```

### Install GDAL

Note: may not need libgdal-dev, need to test.

```
sudo add-apt-repository ppa:ubuntugis/ppa
sudo apt-get install -y libgdal20 libgdal-dev
```

### Setup pyogrio

```
git clone https://github.com/brendan-ward/pyogrio.git
cd pyogrio

pip3 install cython
sudo python3 setup.py install
sudo pip3 install -e .
```

Locally, use `pip freeze > requirements.txt` to snapshot dependencies, and edit by hand.
Make sure to add `gunicorn` (not used locally).

Test the API server to make sure it is working:

```
uvicorn api:app --port 5000
```

## Install Redis

Notes here: https://www.digitalocean.com/community/tutorials/how-to-install-and-secure-redis-on-ubuntu-18-04

```
sudo apt install -y redis-server
sudo vim /etc/redis/redis.conf # change "supervised no" to "supervised systemd"
sudo service nginx restart
```

## Install nginx

```
sudo apt-get install -y nginx
```

-   remove the default config file: `sudo rm /etc/nginx/sites-enabled/default`
-   `sudo cp /home/ubuntu/app/sa-reports/deploy/nginx.conf /etc/nginx/sites-available/sa`
-   `sudo ln -s /etc/nginx/sites-available/sa /etc/nginx/sites-enabled/`
-   `sudo systemctl restart nginx`

## Data

Copy up data to `~/app/sa-reports/data` directory and unzip.

## Environment variables

Copy `.env` to `~/app/sa-reports/.env`

## Setup services

Copy the `deploy/*.service` files from the repo to `/etc/systemd/system/`
Verify that each starts correctly:

-   `sudo service <name> start`
-   `sudo service <name> status`
-   `sudo service <name> stop`

Enable them on restart:

-   `sudo systemctl <name>`

## Services that are running:

-   nginx
-   redis
-   api (gunicorn -> uvicorn)
-   worker (background arq worker)
-   renderer (mbgl-server)

---

### Not used: Install docker

https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-on-ubuntu-18-04

```
apt install -y apt-transport-https ca-certificates curl software-properties-common
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu bionic stable"
apt install -y docker-ce
usermod -aG docker ${USER}   # may need to manually specify user
```

### Dockerized setup

```
docker pull osgeo/gdal:alpine-ultrasmall-latest
docker run -it osgeo/gdal:alpine-ultrasmall-latest sh


# test clone of pyogrio
apk add --no-cache git g++ python3 python3-dev py3-numpy py3-numpy-dev


git clone https://github.com/brendan-ward/pyogrio.git
cd pyogrio

pip3 install cython
python3 setup.py install


```

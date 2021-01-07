# South Atlantic Simple Viewer Deployment - DOI GeoPlatform - Staging

This version is deployed to the DOI GeoPlatform infrastructure,
managed by Zivaro. This includes instructions for setting up the companion project
`secas-blueprint` since both use shared resources provided here.

Docker images are managed using AWS ECR service within that account.

## Initial setup

Setup the AWS CLI v2. Add a profile called `geoplatform-test` to the `~/.aws/credentials`
and `~/.aws/config` files.

## Login to ECR

Set an environment variable for the ECR endpoint:

```
export DOCKER_REGISTRY=<ECR registry URL>/blueprint
```

Fetch token to use ECR:

```
aws ecr get-login-password --region us-east-1 --profile geoplatform-test | docker login --username AWS --password-stdin $DOCKER_REGISTRY
```

## Create a repository for each image

```
aws ecr create-repository --profile geoplatform-test --repository-name blueprint/caddy --image-scanning-configuration scanOnPush=true --encryption-configuration encryptionType=KMS,kmsKey=<ARN of key>

aws ecr create-repository --profile geoplatform-test --repository-name blueprint/redis --image-scanning-configuration scanOnPush=true --encryption-configuration encryptionType=KMS,kmsKey=<ARN of key>

aws ecr create-repository --profile geoplatform-test --repository-name blueprint/mbtileserver --image-scanning-configuration scanOnPush=true --encryption-configuration encryptionType=KMS,kmsKey=<ARN of key>

aws ecr create-repository --profile geoplatform-test --repository-name blueprint/mbgl-renderer --image-scanning-configuration scanOnPush=true --encryption-configuration encryptionType=KMS,kmsKey=<ARN of key>

aws ecr create-repository --profile geoplatform-test --repository-name blueprint/sa-ui-build --image-scanning-configuration scanOnPush=true --encryption-configuration encryptionType=KMS,kmsKey=<ARN of key>

aws ecr create-repository --profile geoplatform-test --repository-name blueprint/blueprint-api --image-scanning-configuration scanOnPush=true --encryption-configuration encryptionType=KMS,kmsKey=<ARN of key>
```

## Push public images from Docker Hub to ECR

First, pull the latest version of all the publicly available images used in this project from Docker Hub.

```
docker-compose pull
```

Tag each public image (update version numbers as appropriate):

```
docker tag caddy/caddy:2.2.1-alpine $DOCKER_REGISTRY/caddy:2.2.1-alpine
docker tag redis:6.0.9-alpine $DOCKER_REGISTRY/redis:6.0.9-alpine
docker tag consbio/mbtileserver:latest $DOCKER_REGISTRY/mbtileserver:latest
docker tag consbio/mbgl-renderer:latest $DOCKER_REGISTRY/mbgl-renderer:latest
```

Push each image:

```
docker push $DOCKER_REGISTRY/caddy:2.2.1-alpine
docker push $DOCKER_REGISTRY/redis:6.0.9-alpine
docker push $DOCKER_REGISTRY/mbtileserver:latest
docker push $DOCKER_REGISTRY/mbgl-renderer:latest
```

## Build and push custom images

Create the UI build image that is used to build the UI on the server.
From within the `ui` folder of the applicable deploy folder:

```bash
docker-compose -f docker-compose.yml build
docker push $DOCKER_REGISTRY/sa-ui-build
```

Create the API / background worker image from the base directory in this repo:
Note: the `PYOGRIO_COMMIT_HASH` must be set to a specific commit hash on that repo.

```bash
docker build -f docker/api/Dockerfile -t blueprint-api:latest --build-arg PYOGRIO_COMMIT_HASH=<hash> .
docker tag blueprint-api:latest $DOCKER_REGISTRY/blueprint-api:latest
docker push $DOCKER_REGISTRY/blueprint-api:latest
```

## Instance setup

Upgrade `docker-compose`:

1. uninstall installation via `apt-get`: `sudo apt-get remove docker-compose`
2. Install using `curl` using link on docker-compose website.

Everything is run as `app` user. Create user and transfer ownership of main directories:

```bash
sudo useradd --create-home app
sudo usermod -aG docker app
sudo chown app:app /var/www
sudo chown app:app /data
usermod --shell /bin/bash app
```

Add current domain user to `app` group:

```bash
sudo usermod -a -G app <domain user>
```

As `app` user:

```bash
rm -rf /var/www/html
mkdir /var/www/southatlantic
mkdir /var/www/southeast
mkdir /data/sa
mkdir /data/se
mkdir /data/tiles
cd ~
git clone https://github.com/astutespruce/sa-blueprint-sv.git
git clone https://github.com/astutespruce/secas-blueprint.git
```

### Environment setup

In `/home/app/sa-blueprint-sv/deploy/gpstaging` create an `.env` file with:

```
DOCKER_REGISTRY=<registry>
COMPOSE_PROJECT_NAME=southatlantic
TEMP_DIR=/tmp/sa-reports
MAPBOX_ACCESS_TOKEN=<mapbox token>
API_TOKEN=<api token>
API_SECRET=<api secret>
LOGGING_LEVEL=DEBUG
REDIS_HOST=redis
REDIS_PORT=6379
MBGL_SERVER_URL=http://renderer/render
ALLOWED_ORIGINS="<hostname>"
SENTRY_DSN=<sentry DSN>
MAP_RENDER_THREADS=1
MAX_JOBS=1
```

### Pull images (to the EC2 instance)

As `app` user:

Create Docker token:

```bash
export DOCKER_REGISTRY=<registry>
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin $DOCKER_REGISTRY
```

Pull images, in `/home/app/deploy/gpstaging/` directory:

```bash
docker-compose pull
```

### Build the UI

Create a `.env.production` file in `/home/app/ui` with the following:

```
GATSBY_MAPBOX_API_TOKEN=<mb token>
GATSBY_API_TOKEN=<api token>

SITE_URL=<site root URL>
SITE_ROOT_PATH=southatlantic
GATSBY_API_HOST=<site root URL>/southatlantic
GATSBY_TILE_HOST=<site root URL>
GATSBY_SENTRY_DSN=<dsn>
GATSBY_GOOGLE_ANALYTICS_ID=<id>

GATSBY_MS_FORM_EMAIL=<email>
GATSBY_MS_FORM_NAME=<name>
GATSBY_MS_FORM_ORG=<org>
GATSBY_MS_FORM_USE=<use>
GATSBY_MS_FORM_AREANAME=<areaname>
GATSBY_MS_FORM_FILENAME=<filename>
```

Note: `--prefix-paths` is required for `gatsby build` to work; this is encapsulated in `build-ui.sh`.

in `/home/app/deploy/gpstaging/ui` directory:

```bash
export DOCKER_REGISTRY=<registry url>
chmod 777 build-ui.sh
docker-compose pull
docker-compose build
./build-ui.sh
```

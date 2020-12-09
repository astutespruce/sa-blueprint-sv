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

```bash
docker-compose -f docker-compose.ui.yml build
docker push $DOCKER_REGISTRY/sa-ui-build
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

In `/home/app/sa-blueprint-sv/deploy/gpstaging` creating a `.env` file with:

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

### Pull images

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

Note: `--prefix-paths` is required for `gatsby build` to work; this is encapsulated in `build-ui.sh`.

in `/home/app/deploy/gpstaging/ui` directory:

```bash
chmod 777 build-ui.sh
docker-compose pull
docker-compose build
./build-ui.sh
```

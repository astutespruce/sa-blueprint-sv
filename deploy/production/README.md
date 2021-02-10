# South Atlantic Simple Viewer Deployment - DOI GeoPlatform - Production

This version is deployed to the DOI GeoPlatform infrastructure,
managed by Zivaro. This includes instructions for setting up the companion project
`secas-blueprint` since both use shared resources provided here.

Docker images are managed using AWS ECR service within the TEST account and shared
with the production account.

## Support

All requests for assistance with the environment go to gishelpdesk @ zivaro.com

Zivaro staff provide uptime monitoring, patching, and management of the AWS infrastructure.

## Docker images

See `deploy/gpstaging/README.md` for information about creating and managing
docker images.

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
cd ~
git clone https://github.com/astutespruce/sa-blueprint-sv.git
git clone https://github.com/astutespruce/secas-blueprint.git
```

### EFS data sync

After transfer of data to EFS mounted at `/data`, change permissions

```
sudo chown -R app:app /data
```

### Environment setup

In `/home/app/sa-blueprint-sv/deploy/production` create an `.env` file with:

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

Create a `.env` file with

```
DOCKER_REGISTRY=<registry url>
```

```bash
chmod 777 build-ui.sh
docker-compose pull
./build-ui.sh
```

## Data

Tiles and data files are loaded up to the test environment first, and then synced by Zivaro staff to the production instance when they have been proofed (using a Rundeck script in their AWS orchestration suite). Put in a
support ticket as specified above to request sync of data from test environment to production.

# South Atlantic Simple Viewer Deployment - Shared Env for SA and Southeast

## Workspace

Everything is run as `ubuntu` user .

Everything happens in the `/home/app` workspace (create it).

Clone `sa-blueprint-sv` (this repo) into `~/app/sa-blueprint-sv`.
Clone `secas-blueprint` into `~/app/secas-blueprint`.

Make root directories:

```bash
sudo mkdir /var/www
sudo chown -R ubuntu:ubuntu /var/www
mkdir /var/www/sa
mkdir /var/www/se
mkdir /data/sa
mkdir /data/se
mkdir /data/tiles
mkdir /data/tiles/sa
mkdir /data/tiles/se
```

## Inputs

Tiles and data files are prepared locally and uploaded for deployment.

Copy contents of local `tiles` directory to appropriate folder under `/data/tiles`.

Copy `inputs` and `results` directories to appropriate folder under `/data`.

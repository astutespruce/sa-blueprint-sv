# South Atlantic Conservation Blueprint Custom Reporting

## ARCHIVED

This project has been superseded by the
[Southeast Blueprint Explorer](https://blueprint.geoplatform.gov/southeast/),
which uses a similar overall approach to visualizing landscape-level priorities
but for a much larger region.

Repository is located at: https://github.com/astutespruce/secas-blueprint

## Development environment

Python dependencies are managed using `poetry`. First, install poetry, then
`poetry install` to install most of them.

`pymgl` requires extra steps on Arm64 architectures because no wheel is yet available.
It is currently built locally in a sibling folder and added as a wheel here.

### Other dependencies

On MacOS, install other dependencies:

- `brew install gdal`
- `brew install pango`

For Macos M1 (Arm64), you also need to setup a symlink for one of the libraries
to be found:

```
sudo ln -s /opt/homebrew/opt/fontconfig/lib/libfontconfig.1.dylib /usr/local/lib/fontconfig-1
```

### Starting background jobs and API server

Background jobs use `arq` which relies on `redis` installed on the host.

On MacOS, start `redis`:

```
redis-server /usr/local/etc/redis.conf
```

To start `arq` with reload capability:

```
arq api.worker.WorkerSettings --watch ./api
```

To start the API in development mode:

```
uvicorn api.api:app --reload --port 5000
```

## Deployment

Deployment configuration is managed in the [secas-docker](https://github.com/astutespruce/secas-docker) repository.

## Credits

This project is developed under a grant from the U.S. Fish and Wildlife Service
to support the [Southeast Conservation Adaptation Strategy](https://secassoutheast.org/).

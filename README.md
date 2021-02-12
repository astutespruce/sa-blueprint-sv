# South Atlantic Conservation Blueprint Custom Reporting

## Development environment

Install python dependencies using `pipenv` and JS dependencies (in `/ui`) using NPM.

### Installation issues

Weasyprint is used to generate PDF files. It depends on `cairocffi` which sometimes does not install correctly.

Run `pip install --no-cache-dir cairocffi` to correctly install it.

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

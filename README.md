# Multi-user Single-room chatting

### `#aiohttp`, `#redis-py`, `#asyncio`, `#React.ts`

## Made by [금나연](https://github.com/NayeonKeum) [nkeum@lablup.com](nkeum@lablup.com)

## Features

- Can chat with multiple users in a single chatroom
  ![features](./src/features.gif)

## Execute

## How to execute

### For Use-only

**1. Check conditions**

- `docker`, `docker-compose` should be installed
- versions
  ![docker-versions](./src/docker-versions.png)

**2. Use current docker-compose.yml file**

- There is two kinds of docker-compose.yml files in `./docker-composes` directory
  - `docker-compose-prod.yml(default)`: for use-only(uses dockerhub images)
  - `docker-compose-dev.yml`: for develop(uses local diretories to build images)

**3. Execute with docker compose**

```bash
docker compose build && docker compose up
```

### For Develop

Recommended to freely upgrade this(add features, report bugs, ...) :smile:!

**1. Check conditions**

- `docker`, `docker-compose` should be installed
  ![docker-versions](./src/docker-versions.png)
- If wanting to execute locally, please check `pythonv3.11`(and other requirements in `./WAS/requirements.txt`), `npm v9.6.6`, `yarn v1.22.19`, `node v19.8.1`.(I'm using pyenv)

**2. Use current docker-compose.yml file**

- There is two kinds of docker-compose.yml files in `./docker-composes` directory
  - `docker-compose-prod.yml(default)`: for use-only(uses dockerhub images)
  - `docker-compose-dev.yml`: for develop(uses local diretories to build images)
- Use `docker-compose-dev.yml` in this case.

**3. Execute with docker compose**

```bash
docker compose build && docker compose up
```

**4. Info**

- There is a Docker CI for web, was server each made by github actions.
- Checkout `./.github/workflows/was-image-build.yml` and `./.github/workflows/web-image-build.yml`
  - `./WEB/` for web-frontend(React.ts)
  - `./WAS/` for backend-server(Python-aiohttp)

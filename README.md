# hermes-builder

GitHub Actions builder for NousResearch/hermes-agent. Pushes the resulting image
to `ghcr.io/moonscoder63/hermes-agent:isolated`.

The namecheap VPS pulls the image from GHCR (its outbound bandwidth to GitHub
is ~10 MB/s), bypassing the slow direct upload from the operator's machine.

## Trigger a build

```sh
gh workflow run build-hermes-image -R moonscoder63/hermes-builder
gh run watch -R moonscoder63/hermes-builder
```

Or via the Actions tab in the GitHub UI.

## Use a specific upstream commit

```sh
gh workflow run build-hermes-image -R moonscoder63/hermes-builder \
    -f hermes_ref=v0.13.0
```

## Pull on server

```sh
docker pull ghcr.io/moonscoder63/hermes-agent:isolated
docker tag ghcr.io/moonscoder63/hermes-agent:isolated hermes-agent:isolated
```

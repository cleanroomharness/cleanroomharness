# Kubernetes Deployments

Three deployment tiers, one architecture:

| Tier | Path | When |
|------|------|------|
| **Appliance** | `infra/k8s/appliance/appliance.yaml` or `docker-compose.appliance.yml` | One container with everything (API + Ollama + SQLite); maximum air-gap portability |
| **Lean** | `docker compose up --build` (repo root) | Local development, demos |
| **K3s** | `infra/k8s/overlays/k3s` | Single node, edge, air-gapped, small regulated environments |
| **K8s** | `infra/k8s/overlays/k8s` | Multi-node enterprise clusters (EKS/AKS/GKE/on-prem) |

The kustomize `base/` holds the stack (API, LiteLLM, Postgres+pgvector,
Qdrant, Redis); overlays only change what differs per environment.

## K3s (single node / edge / air-gap-friendly)

K3s ships with Traefik ingress and the `local-path` default storage class,
which this overlay relies on.

```bash
# 1. Build the API image and import it into K3s
docker build -t cleanroom-harness-api:0.1.0 .
docker save cleanroom-harness-api:0.1.0 | sudo k3s ctr images import -

# 2. Deploy
kubectl apply -k infra/k8s/overlays/k3s

# 3. Reach it (Ingress host is harness.local)
echo "127.0.0.1 harness.local" | sudo tee -a /etc/hosts
curl http://harness.local/health
# or skip ingress:
kubectl -n cleanroom-harness port-forward svc/api 8080:8080
```

## Air-gapped deployment

The stack is built to run fully disconnected:

- **No phone-home.** Qdrant telemetry is disabled (`QDRANT__TELEMETRY_DISABLED`), LiteLLM telemetry is off in `files/litellm-config.yaml`, and the API makes no external calls. OpenTelemetry defaults to console output; point OTLP only at an in-boundary collector.
- **Pinned images.** All image tags are pinned versions (no `latest`/`main-stable`), so the bundle you scanned is the bundle you run.
- **Transfer bundle.** On a connected host:

  ```bash
  make airgap-bundle      # full stack: API image + pinned service images
  make appliance-bundle   # single image with model weights baked in
                          # (both write tarballs + SHA256SUMS + IMPORT.md to dist/airgap/)
  ```

  The appliance bundle is the simplest boundary crossing: one tarball, one
  `docker load` (or `k3s ctr images import`), zero runtime fetches —
  `kubectl apply -f infra/k8s/appliance/appliance.yaml` and done.

  Carry `dist/airgap/` across the boundary and follow its `IMPORT.md`:
  verify checksums, `k3s ctr images import` (or `docker load` /
  in-boundary registry push), copy the Ollama model store
  (`~/.ollama/models` after `ollama pull llama3.2:3b` on the connected
  host), then `kubectl apply -k infra/k8s/overlays/k3s` or
  `docker compose up --no-build`.

- **Models stay inside.** Keep the LiteLLM model list pointing only at in-boundary endpoints (e.g. an Ollama service inside the cluster). Adding an external provider is a config change that should go through your change-control process.

## Generic Kubernetes (enterprise)

```bash
# Push the image somewhere your cluster can pull from, then set it in
# overlays/k8s/kustomization.yaml (images: transformer).
docker build -t registry.example.com/cleanroom-harness-api:0.1.0 .
docker push registry.example.com/cleanroom-harness-api:0.1.0

kubectl apply -k infra/k8s/overlays/k8s
```

The overlay runs 2 API replicas and an nginx-class Ingress
(`harness.example.com`) — adjust host, TLS, and ingress class per cluster.

## Secrets — read before any real deployment

`base/kustomization.yaml` generates `harness-dev-config` with **dev-only
placeholder values** so the reference stack starts out of the box. In any real
deployment, replace that generator with a proper secret mechanism (External
Secrets Operator, Sealed Secrets, SOPS, or your cloud's secret manager) and
rotate the Postgres and LiteLLM values. Never commit real secrets — in this
repo or your private fork.

## Ollama / models

The default model (`ollama/llama3.2:3b`) expects Ollama. In-cluster options:
run an Ollama Deployment and set its service URL as `api_base` in the LiteLLM
ConfigMap (`base/files/litellm-config.yaml`), or point LiteLLM at approved
external endpoints per your deployment's policy.

Note: `base/files/` contains copies of `infra/litellm/config.yaml` and
`infra/postgres/init.sql` (kustomize cannot reference files outside its
directory). If you change the originals, update the copies.

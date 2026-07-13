# Kubernetes Deployments

Three deployment tiers, one architecture:

| Tier | Path | When |
|------|------|------|
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

**Air-gapped notes:** pre-pull `ghcr.io/berriai/litellm:main-stable`,
`pgvector/pgvector:pg16`, `qdrant/qdrant`, and `redis:7-alpine` the same way
(`docker save | k3s ctr images import -`), and point the LiteLLM config only
at in-boundary model endpoints (e.g. an Ollama service inside the cluster).

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

#!/usr/bin/env bash
# Build an air-gap transfer bundle on a CONNECTED host.
#
# Produces a directory of image tarballs with checksums and import
# instructions, ready to carry across the boundary and load on the
# disconnected host (docker load, or k3s ctr images import).
#
# Usage: scripts/build_airgap_bundle.sh [output-dir]   (default: dist/airgap)
set -euo pipefail

cd "$(dirname "$0")/.."

OUT="${1:-dist/airgap}"
API_IMAGE="cleanroom-harness-api:0.1.0"

# Keep in sync with docker-compose.yml and infra/k8s/base/*.yaml.
SERVICE_IMAGES=(
  "ghcr.io/berriai/litellm:main-v1.66.0-stable"
  "pgvector/pgvector:0.8.5-pg16"
  "qdrant/qdrant:v1.18.2"
  "redis:7.4.9-alpine"
)

mkdir -p "$OUT"

echo "==> Building $API_IMAGE"
docker build -t "$API_IMAGE" .

for image in "${SERVICE_IMAGES[@]}"; do
  echo "==> Pulling $image"
  docker pull "$image"
done

save_image() {
  local image="$1"
  local file
  file="$OUT/$(echo "$image" | tr '/:' '__').tar"
  echo "==> Saving $image -> $file"
  docker save "$image" -o "$file"
}

save_image "$API_IMAGE"
for image in "${SERVICE_IMAGES[@]}"; do
  save_image "$image"
done

echo "==> Writing checksums"
(
  cd "$OUT"
  if command -v sha256sum >/dev/null 2>&1; then
    sha256sum ./*.tar > SHA256SUMS
  else
    shasum -a 256 ./*.tar > SHA256SUMS
  fi
)

cat > "$OUT/IMPORT.md" <<'EOF'
# Importing this bundle on the air-gapped host

1. Verify checksums:

       sha256sum -c SHA256SUMS      # or: shasum -a 256 -c SHA256SUMS

2. Load every image.

   Docker Compose host:

       for f in *.tar; do docker load -i "$f"; done

   K3s node:

       for f in *.tar; do sudo k3s ctr images import "$f"; done

   Generic Kubernetes: push the images into your in-boundary registry
   (docker load, retag, docker push), then set the registry in
   infra/k8s/overlays/k8s/kustomization.yaml (images: transformer).

3. Models (default: ollama/llama3.2:3b). On a connected host run
   `ollama pull llama3.2:3b`, then copy the Ollama model store
   (~/.ollama/models, or $OLLAMA_MODELS if set) to the same path on the
   air-gapped host running Ollama.

4. Start the stack without touching any registry:

       cp .env.example .env
       docker compose up --no-build          # Compose
       kubectl apply -k infra/k8s/overlays/k3s   # K3s

No component phones home: Qdrant telemetry is disabled via
QDRANT__TELEMETRY_DISABLED, LiteLLM telemetry is off in its config, and the
API makes no external calls. Keep the LiteLLM model list pointing only at
in-boundary endpoints.
EOF

echo ""
echo "Bundle ready in $OUT/ — carry the directory across the boundary and follow IMPORT.md."

#!/usr/bin/env bash
# Build an air-gap transfer bundle on a CONNECTED host.
#
# Full stack (default): every image the Compose/K8s stack needs.
# Appliance (--appliance): ONE image containing the API + Ollama model
# server, with model weights baked in (BAKE_MODEL, default llama3.2:3b).
#
# Usage:
#   scripts/build_airgap_bundle.sh [output-dir]                # full stack
#   scripts/build_airgap_bundle.sh --appliance [output-dir]    # single image
#   BAKE_MODEL=llama3.2:3b scripts/build_airgap_bundle.sh --appliance
#
# Output: image tarballs + SHA256SUMS + IMPORT.md, ready to carry across
# the boundary and load (docker load / k3s ctr images import).
set -euo pipefail

cd "$(dirname "$0")/.."

MODE="full"
if [ "${1:-}" = "--appliance" ]; then
  MODE="appliance"
  shift
fi
OUT="${1:-dist/airgap}"

API_IMAGE="cleanroom-harness-api:0.1.0"
APPLIANCE_IMAGE="cleanroom-harness-appliance:0.1.0"
BAKE_MODEL="${BAKE_MODEL:-llama3.2:3b}"

# Keep in sync with docker-compose.yml and infra/k8s/base/*.yaml.
SERVICE_IMAGES=(
  "ghcr.io/berriai/litellm:main-v1.66.0-stable"
  "pgvector/pgvector:0.8.5-pg16"
  "qdrant/qdrant:v1.18.2"
  "redis:7.4.9-alpine"
)

mkdir -p "$OUT"

save_image() {
  local image="$1"
  local file
  file="$OUT/$(echo "$image" | tr '/:' '__').tar"
  echo "==> Saving $image -> $file"
  docker save "$image" -o "$file"
}

if [ "$MODE" = "appliance" ]; then
  echo "==> Building $APPLIANCE_IMAGE (baking model: $BAKE_MODEL)"
  docker build -f Dockerfile.appliance --build-arg BAKE_MODEL="$BAKE_MODEL" \
    -t "$APPLIANCE_IMAGE" .
  save_image "$APPLIANCE_IMAGE"
else
  echo "==> Building $API_IMAGE"
  docker build -t "$API_IMAGE" .
  for image in "${SERVICE_IMAGES[@]}"; do
    echo "==> Pulling $image"
    docker pull "$image"
  done
  save_image "$API_IMAGE"
  for image in "${SERVICE_IMAGES[@]}"; do
    save_image "$image"
  done
fi

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

   Docker host:

       for f in *.tar; do docker load -i "$f"; done

   K3s node:

       for f in *.tar; do sudo k3s ctr images import "$f"; done

   Generic Kubernetes: push the images into your in-boundary registry
   (docker load, retag, docker push), then set the registry in
   infra/k8s/overlays/k8s/kustomization.yaml (images: transformer).

3. Start the stack.

   Appliance bundle (one image, model weights baked in — nothing else needed):

       docker run --init -d -p 8080:8080 -v appliancedata:/data \
         cleanroom-harness-appliance:0.1.0
       # or: docker compose -f docker-compose.appliance.yml up --no-build
       # or: kubectl apply -f infra/k8s/appliance/appliance.yaml

   Full-stack bundle:

       cp .env.example .env
       docker compose up --no-build              # Compose
       kubectl apply -k infra/k8s/overlays/k3s   # K3s

   Full-stack models: on a connected host run `ollama pull llama3.2:3b`,
   then copy the Ollama model store (~/.ollama/models, or $OLLAMA_MODELS)
   to the air-gapped host running Ollama.

No component phones home: Qdrant telemetry is disabled, LiteLLM telemetry is
off in its config, and the API makes no external calls. Keep model endpoints
in-boundary only.
EOF

echo ""
echo "Bundle ready in $OUT/ — carry the directory across the boundary and follow IMPORT.md."

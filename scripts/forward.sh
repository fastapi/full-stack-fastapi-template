#!/usr/bin/env sh

# Exit on error
set -e

# Config
HELM_CHART_DIR="./kubernetes/charts/sdp"
RELEASE_NAME="SDP"
BACKEND_PORT=8000
FRONTEND_PORT=5173

# Get pod names using go-template
echo "🔍 Getting pod names..."
PODS=$(kubectl get pods -o go-template --template '{{range .items}}{{.metadata.name}}{{"\n"}}{{end}}')

# Identify backend and frontend pods
BACKEND_POD=""
FRONTEND_POD=""

for pod in $PODS; do
  if echo "$pod" | grep -q "backend"; then
    BACKEND_POD="$pod"
  elif echo "$pod" | grep -q "frontend"; then
    FRONTEND_POD="$pod"
  fi
done

if [ -z "$BACKEND_POD" ]; then
  echo "❌ Could not find backend pod"
  exit 1
fi

if [ -z "$FRONTEND_POD" ]; then
  echo "❌ Could not find frontend pod"
  exit 1
fi

echo "✅ Backend pod: $BACKEND_POD"
echo "✅ Frontend pod: $FRONTEND_POD"

# Start port forwarding
echo "🔌 Starting port forwarding..."
echo "🌐 Backend API: http://localhost:$BACKEND_PORT"
echo "🖥️ Frontend: http://localhost:$FRONTEND_PORT"

kubectl port-forward pod/$BACKEND_POD $BACKEND_PORT:8000 &
BACKEND_PID=$!

kubectl port-forward pod/$FRONTEND_POD $FRONTEND_PORT:80 &
FRONTEND_PID=$!

# Cleanup on exit
cleanup() {
  echo "🛑 Stopping port forwarding..."
  kill $BACKEND_PID $FRONTEND_PID 2>/dev/null || true
  exit 0
}
trap cleanup INT

# Keep running
echo "🎯 Press Ctrl+C to stop"
wait
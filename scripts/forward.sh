#!/usr/bin/env sh

# Exit on error
set -e

# Config
HELM_CHART_DIR="./kubernetes/charts/sdp"
RELEASE_NAME="SDP"
BACKEND_PORT=8000
FRONTEND_PORT=5173
ADMINER_PORT=8080

# Get pod names using go-template
echo "🔍 Getting pod names..."
PODS=$(kubectl get pods -o go-template --template '{{range .items}}{{.metadata.name}}{{"\n"}}{{end}}')

# Identify backend, frontend, and adminer pods
BACKEND_POD=""
FRONTEND_POD=""
ADMINER_POD=""

for pod in $PODS; do
  if echo "$pod" | grep -q "backend"; then
    BACKEND_POD="$pod"
  elif echo "$pod" | grep -q "frontend"; then
    FRONTEND_POD="$pod"
  elif echo "$pod" | grep -q "adminer"; then
    ADMINER_POD="$pod"
  fi
done

# Report found pods
if [ -z "$BACKEND_POD" ]; then
  echo "⚠️ Could not find backend pod, skipping..."
else
  echo "✅ Backend pod: $BACKEND_POD"
fi

if [ -z "$FRONTEND_POD" ]; then
  echo "⚠️ Could not find frontend pod, skipping..."
else
  echo "✅ Frontend pod: $FRONTEND_POD"
fi

if [ -z "$ADMINER_POD" ]; then
  echo "⚠️ Could not find adminer pod, skipping..."
else
  echo "✅ Adminer pod: $ADMINER_POD"
fi

# Start port forwarding for available pods
echo "🔌 Starting port forwarding..."

if [ -n "$BACKEND_POD" ]; then
  echo "🌐 Backend API: http://localhost:$BACKEND_PORT"
  kubectl port-forward pod/$BACKEND_POD $BACKEND_PORT:8000 &
  BACKEND_PID=$!
else
  BACKEND_PID=""
fi

if [ -n "$FRONTEND_POD" ]; then
  echo "🖥️ Frontend: http://localhost:$FRONTEND_PORT"
  kubectl port-forward pod/$FRONTEND_POD $FRONTEND_PORT:80 &
  FRONTEND_PID=$!
else
  FRONTEND_PID=""
fi

if [ -n "$ADMINER_POD" ]; then
  echo "🛠️ Adminer: http://localhost:$ADMINER_PORT"
  kubectl port-forward pod/$ADMINER_POD $ADMINER_PORT:80 &
  ADMINER_PID=$!
else
  ADMINER_PID=""
fi

# Cleanup on exit
cleanup() {
  echo "🛑 Stopping port forwarding..."
  # Only kill PIDs that exist
  [ -n "$BACKEND_PID" ] && kill $BACKEND_PID 2>/dev/null || true
  [ -n "$FRONTEND_PID" ] && kill $FRONTEND_PID 2>/dev/null || true
  [ -n "$ADMINER_PID" ] && kill $ADMINER_PID 2>/dev/null || true
  exit 0
}
trap cleanup INT

# Keep running
echo "🎯 Press Ctrl+C to stop"
wait
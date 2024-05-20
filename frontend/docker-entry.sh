#!/bin/sh
if [ -z "$FRONTEND_API_TARGET" ]; then
  echo "Error: FRONTEND_API_TARGET variable is not set."
  exit 1
fi
# let's choose the correct nginx.conf file
if [ -z "$TRAEFIK" ]; then
    echo "NOT USING TRAEFIK BUT PLAIN NGINX INSTEAD"
    cp /etc/nginx/conf.d/nginx-standalone.conf /etc/nginx/conf.d/default.conf
else
    echo "USING TRAEFIK"
    cp /etc/nginx/conf.d/nginx-traefik.conf /etc/nginx/conf.d/default.conf    
fi
# replacing Vite's static env vars with injected one
echo "SUBSTITUTING FRONTEND TARGET DOMAIN WITH ${FRONTEND_API_TARGET}"
find "/usr/share/nginx/html" -type f -name "*.js" | while read file; do
    perl -pi -e 's|\Qhttp://localhost\E|$ENV{FRONTEND_API_TARGET}|g' $file
done
nginx -g "daemon off;"

FROM nginx:alpine

# Metadata
LABEL version="firmware-0.4.91-mh-600a0df-20251104-155459-mh-deeabe4-20251224-041248"
LABEL build_date="2025-12-24T04:12:48Z"
LABEL description="Custom Meshtastic Firmware Backend"

# Install additional tools for health checks
RUN apk add --no-cache curl jq

# Copy content
COPY firmware/ /usr/share/nginx/html/firmware/
COPY data/ /usr/share/nginx/html/data/
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost/data/device-firmware-mapping.json || exit 1

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]

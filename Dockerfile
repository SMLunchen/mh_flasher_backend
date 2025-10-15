FROM nginx:alpine

# Metadata
LABEL version="dev-d8d48e5-20251015-183708"
LABEL build_date="2025-10-15T18:37:08Z"
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

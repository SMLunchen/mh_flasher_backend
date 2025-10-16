FROM nginx:alpine

# Metadata
LABEL version="0.4.91-mh-543a00b-20251016-034443"
LABEL build_date=""
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

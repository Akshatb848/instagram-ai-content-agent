FROM n8nio/n8n:1.121.0
USER root
COPY n8n/workflows /opt/project-workflows
USER node
HEALTHCHECK --interval=30s --timeout=5s --retries=3 CMD wget -q -O- http://127.0.0.1:5678/healthz || exit 1

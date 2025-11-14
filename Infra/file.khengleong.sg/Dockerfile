FROM nginx:alpine

# Copy custom nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

# Create directory for storage files
RUN mkdir -p /mnt/data/hoangpt/report-automation-project/API.FastPy/storage

# Expose port 8088
EXPOSE 8088

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8088/health || exit 1

# Start nginx
CMD ["nginx", "-g", "daemon off;"]

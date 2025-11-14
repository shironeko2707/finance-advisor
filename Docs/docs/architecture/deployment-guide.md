# Deployment Guide
*Comprehensive deployment and infrastructure setup guide for Khengleong system*

## Overview

This guide provides step-by-step instructions for deploying the Khengleong AI Report Generation Platform in production environments. It covers infrastructure setup, application deployment, and operational procedures.

## Table of Contents

1. [Infrastructure Requirements](#1-infrastructure-requirements)
2. [Environment Setup](#2-environment-setup)
3. [Container Configuration](#3-container-configuration)
4. [Kubernetes Deployment](#4-kubernetes-deployment)
5. [Database Setup](#5-database-setup)
6. [Security Configuration](#6-security-configuration)
7. [Monitoring Setup](#7-monitoring-setup)
8. [CI/CD Pipeline](#8-cicd-pipeline)
9. [Backup and Recovery](#9-backup-and-recovery)
10. [Troubleshooting](#10-troubleshooting)

## 1. Infrastructure Requirements

### 1.1 Minimum System Requirements

#### Production Environment
```yaml
# Application Servers (3 nodes minimum)
CPU: 8 cores per node
Memory: 32GB per node
Storage: 500GB SSD per node
Network: 10Gbps

# Database Servers (2 nodes for HA)
CPU: 16 cores per node
Memory: 64GB per node
Storage: 2TB NVMe SSD per node
Network: 10Gbps

# AI Processing Servers (2 nodes with GPU)
CPU: 16 cores per node
Memory: 64GB per node
GPU: NVIDIA V100 or A100
Storage: 1TB NVMe SSD per node
Network: 10Gbps

# Load Balancer
CPU: 4 cores
Memory: 16GB
Network: 10Gbps with multiple NICs
```

#### Development Environment
```yaml
# Single server setup
CPU: 8 cores
Memory: 32GB
Storage: 500GB SSD
Docker: Latest version
Kubernetes: minikube or k3s
```

### 1.2 Cloud Infrastructure (AWS Example)

```yaml
# VPC Configuration
VPC:
  CIDR: 10.0.0.0/16
  Availability Zones: 3

# Subnets
Public Subnets:
  - 10.0.1.0/24 (AZ-a)
  - 10.0.2.0/24 (AZ-b)
  - 10.0.3.0/24 (AZ-c)

Private Subnets:
  - 10.0.11.0/24 (AZ-a)
  - 10.0.12.0/24 (AZ-b)
  - 10.0.13.0/24 (AZ-c)

Database Subnets:
  - 10.0.21.0/24 (AZ-a)
  - 10.0.22.0/24 (AZ-b)
  - 10.0.23.0/24 (AZ-c)

# EC2 Instances
Application Nodes:
  Type: c5.2xlarge
  Count: 3
  Storage: 500GB gp3

AI Processing Nodes:
  Type: p3.2xlarge
  Count: 2
  Storage: 1TB gp3

# RDS Configuration
Database:
  Engine: PostgreSQL 14
  Instance: db.r5.2xlarge
  Multi-AZ: true
  Storage: 1TB gp3

# ElastiCache
Cache:
  Engine: Redis 6.2
  Node Type: cache.r6g.large
  Cluster Mode: enabled

# EKS Cluster
Kubernetes:
  Version: 1.24
  Node Groups: 3
  Managed: true
```

## 2. Environment Setup

### 2.1 Terraform Infrastructure as Code

```hcl
# main.tf
provider "aws" {
  region = var.aws_region
}

# VPC
resource "aws_vpc" "Khengleong_vpc" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name = "Khengleong-vpc"
    Environment = var.environment
  }
}

# Internet Gateway
resource "aws_internet_gateway" "Khengleong_igw" {
  vpc_id = aws_vpc.Khengleong_vpc.id

  tags = {
    Name = "Khengleong-igw"
  }
}

# EKS Cluster
resource "aws_eks_cluster" "Khengleong_cluster" {
  name     = "Khengleong-cluster"
  role_arn = aws_iam_role.eks_cluster_role.arn
  version  = "1.24"

  vpc_config {
    subnet_ids         = concat(aws_subnet.private_subnets[*].id, aws_subnet.public_subnets[*].id)
    endpoint_private_access = true
    endpoint_public_access  = true
  }

  depends_on = [
    aws_iam_role_policy_attachment.eks_cluster_policy,
  ]
}

# RDS Instance
resource "aws_db_instance" "Khengleong_db" {
  identifier = "Khengleong-db"
  engine     = "postgres"
  engine_version = "14.6"
  instance_class = "db.r5.2xlarge"
  
  allocated_storage     = 1000
  max_allocated_storage = 5000
  storage_type         = "gp3"
  storage_encrypted    = true

  db_name  = "Khengleong"
  username = var.db_username
  password = var.db_password

  vpc_security_group_ids = [aws_security_group.rds_sg.id]
  db_subnet_group_name   = aws_db_subnet_group.Khengleong_db_subnet_group.name

  backup_retention_period = 7
  backup_window          = "03:00-04:00"
  maintenance_window     = "Sun:04:00-Sun:05:00"

  multi_az = true
  
  tags = {
    Name = "Khengleong-db"
    Environment = var.environment
  }
}

# ElastiCache Redis Cluster
resource "aws_elasticache_replication_group" "Khengleong_redis" {
  replication_group_id       = "Khengleong-redis"
  description                = "Redis cluster for Khengleong"
  
  node_type                  = "cache.r6g.large"
  port                       = 6379
  parameter_group_name       = "default.redis6.x"
  
  num_cache_clusters         = 3
  automatic_failover_enabled = true
  multi_az_enabled          = true
  
  subnet_group_name = aws_elasticache_subnet_group.Khengleong_cache_subnet_group.name
  security_group_ids = [aws_security_group.elasticache_sg.id]
  
  at_rest_encryption_enabled = true
  transit_encryption_enabled = true
  
  tags = {
    Name = "Khengleong-redis"
    Environment = var.environment
  }
}
```

### 2.2 Environment Variables

```bash
# .env.production
NODE_ENV=production
APP_PORT=3000

# Database
DATABASE_URL=postgresql://username:password@host:5432/Khengleong
DATABASE_POOL_MIN=5
DATABASE_POOL_MAX=50

# Redis
REDIS_URL=redis://Khengleong-redis.cache.amazonaws.com:6379
REDIS_TTL=3600

# File Storage
AWS_REGION=us-west-2
AWS_S3_BUCKET=Khengleong-files
AWS_S3_REGION=us-west-2

# AI Services
AI_SERVICE_URL=http://ai-service:8000
AI_MODEL_PATH=/models
GPU_ENABLED=true

# Security
JWT_SECRET=your-super-secure-jwt-secret
JWT_EXPIRATION=3600
ENCRYPTION_KEY=your-256-bit-encryption-key

# Monitoring
LOG_LEVEL=info
ELASTICSEARCH_URL=https://elasticsearch.Khengleong.com:9200
PROMETHEUS_ENDPOINT=http://prometheus:9090

# External Services
SENTRY_DSN=https://your-sentry-dsn
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...
```

## 3. Container Configuration

### 3.1 Docker Compose for Development

```yaml
# docker-compose.yml
version: '3.8'

services:
  # API Gateway
  api-gateway:
    image: kong:latest
    ports:
      - "8000:8000"
      - "8443:8443"
      - "8001:8001"
      - "8444:8444"
    environment:
      KONG_DATABASE: postgres
      KONG_PG_HOST: postgres
      KONG_PG_USER: kong
      KONG_PG_PASSWORD: kong
      KONG_PROXY_ACCESS_LOG: /dev/stdout
      KONG_ADMIN_ACCESS_LOG: /dev/stdout
      KONG_PROXY_ERROR_LOG: /dev/stderr
      KONG_ADMIN_ERROR_LOG: /dev/stderr
      KONG_ADMIN_LISTEN: 0.0.0.0:8001
    depends_on:
      - postgres

  # File Upload Service
  file-upload-service:
    build:
      context: ./services/file-upload
      dockerfile: Dockerfile
    environment:
      - NODE_ENV=development
      - DATABASE_URL=postgresql://Khengleong:password@postgres:5432/Khengleong
      - REDIS_URL=redis://redis:6379
      - AWS_S3_BUCKET=Khengleong-dev-files
    volumes:
      - ./services/file-upload:/app
      - /app/node_modules
    depends_on:
      - postgres
      - redis

  # AI Extraction Service
  ai-extraction-service:
    build:
      context: ./services/ai-extraction
      dockerfile: Dockerfile
    environment:
      - PYTHONPATH=/app
      - DATABASE_URL=postgresql://Khengleong:password@postgres:5432/Khengleong
      - REDIS_URL=redis://redis:6379
      - MODEL_PATH=/models
    volumes:
      - ./services/ai-extraction:/app
      - ./models:/models
    depends_on:
      - postgres
      - redis
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]

  # Template Service
  template-service:
    build:
      context: ./services/template
      dockerfile: Dockerfile
    environment:
      - SPRING_PROFILES_ACTIVE=development
      - DATABASE_URL=postgresql://Khengleong:password@postgres:5432/Khengleong
      - REDIS_URL=redis://redis:6379
    depends_on:
      - postgres
      - redis

  # Report Service
  report-service:
    build:
      context: ./services/report
      dockerfile: Dockerfile
    environment:
      - NODE_ENV=development
      - DATABASE_URL=postgresql://Khengleong:password@postgres:5432/Khengleong
      - REDIS_URL=redis://redis:6379
    depends_on:
      - postgres
      - redis

  # Auth Service
  auth-service:
    build:
      context: ./services/auth
      dockerfile: Dockerfile
    environment:
      - NODE_ENV=development
      - DATABASE_URL=postgresql://Khengleong:password@postgres:5432/Khengleong
      - REDIS_URL=redis://redis:6379
      - JWT_SECRET=dev-secret-key
    depends_on:
      - postgres
      - redis

  # Frontend
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      - REACT_APP_API_URL=http://localhost:8000
    volumes:
      - ./frontend:/app
      - /app/node_modules

  # Database
  postgres:
    image: postgres:14
    environment:
      POSTGRES_DB: Khengleong
      POSTGRES_USER: Khengleong
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./database/init.sql:/docker-entrypoint-initdb.d/init.sql
    ports:
      - "5432:5432"

  # Redis
  redis:
    image: redis:6-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  # Elasticsearch
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:7.17.0
    environment:
      - discovery.type=single-node
      - "ES_JAVA_OPTS=-Xms512m -Xmx512m"
    volumes:
      - elasticsearch_data:/usr/share/elasticsearch/data
    ports:
      - "9200:9200"

  # Kibana
  kibana:
    image: docker.elastic.co/kibana/kibana:7.17.0
    environment:
      ELASTICSEARCH_HOSTS: http://elasticsearch:9200
    ports:
      - "5601:5601"
    depends_on:
      - elasticsearch

volumes:
  postgres_data:
  redis_data:
  elasticsearch_data:
```

### 3.2 Production Dockerfiles

#### File Upload Service Dockerfile
```dockerfile
# services/file-upload/Dockerfile
FROM node:18-alpine AS builder

WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

FROM node:18-alpine AS runtime

RUN addgroup -g 1001 -S nodejs
RUN adduser -S nodeuser -u 1001

WORKDIR /app

COPY --from=builder /app/node_modules ./node_modules
COPY --chown=nodeuser:nodejs . .

USER nodeuser

EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD node healthcheck.js

CMD ["node", "src/index.js"]
```

#### AI Extraction Service Dockerfile
```dockerfile
# services/ai-extraction/Dockerfile
FROM nvidia/cuda:11.8-runtime-ubuntu20.04 AS base

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y \
    python3.9 \
    python3-pip \
    python3-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

FROM base AS runtime

RUN adduser --disabled-password --gecos '' appuser
COPY --chown=appuser:appuser . .

USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD python3 -c "import requests; requests.get('http://localhost:8000/health')"

CMD ["python3", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 4. Kubernetes Deployment

### 4.1 Namespace and ConfigMaps

```yaml
# k8s/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: Khengleong
  labels:
    name: Khengleong
---
# k8s/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: Khengleong-config
  namespace: Khengleong
data:
  DATABASE_HOST: "Khengleong-db.cluster-xyz.region.rds.amazonaws.com"
  DATABASE_PORT: "5432"
  DATABASE_NAME: "Khengleong"
  REDIS_HOST: "Khengleong-redis.cache.amazonaws.com"
  REDIS_PORT: "6379"
  LOG_LEVEL: "info"
  NODE_ENV: "production"
```

### 4.2 Secrets

```yaml
# k8s/secrets.yaml
apiVersion: v1
kind: Secret
metadata:
  name: Khengleong-secrets
  namespace: Khengleong
type: Opaque
data:
  DATABASE_PASSWORD: <base64-encoded-password>
  JWT_SECRET: <base64-encoded-jwt-secret>
  ENCRYPTION_KEY: <base64-encoded-encryption-key>
  AWS_ACCESS_KEY_ID: <base64-encoded-aws-access-key>
  AWS_SECRET_ACCESS_KEY: <base64-encoded-aws-secret-key>
```

### 4.3 Service Deployments

#### File Upload Service
```yaml
# k8s/file-upload-service.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: file-upload-service
  namespace: Khengleong
spec:
  replicas: 3
  selector:
    matchLabels:
      app: file-upload-service
  template:
    metadata:
      labels:
        app: file-upload-service
    spec:
      containers:
      - name: file-upload-service
        image: Khengleong/file-upload-service:v1.0.0
        ports:
        - containerPort: 3000
        env:
        - name: NODE_ENV
          valueFrom:
            configMapKeyRef:
              name: Khengleong-config
              key: NODE_ENV
        - name: DATABASE_PASSWORD
          valueFrom:
            secretKeyRef:
              name: Khengleong-secrets
              key: DATABASE_PASSWORD
        envFrom:
        - configMapRef:
            name: Khengleong-config
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 3000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 3000
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: file-upload-service
  namespace: Khengleong
spec:
  selector:
    app: file-upload-service
  ports:
  - protocol: TCP
    port: 80
    targetPort: 3000
  type: ClusterIP
```

#### AI Extraction Service
```yaml
# k8s/ai-extraction-service.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ai-extraction-service
  namespace: Khengleong
spec:
  replicas: 2
  selector:
    matchLabels:
      app: ai-extraction-service
  template:
    metadata:
      labels:
        app: ai-extraction-service
    spec:
      nodeSelector:
        accelerator: nvidia-tesla-v100
      containers:
      - name: ai-extraction-service
        image: Khengleong/ai-extraction-service:v1.0.0
        ports:
        - containerPort: 8000
        resources:
          requests:
            memory: "4Gi"
            cpu: "2"
            nvidia.com/gpu: 1
          limits:
            memory: "8Gi"
            cpu: "4"
            nvidia.com/gpu: 1
        env:
        - name: MODEL_PATH
          value: "/models"
        envFrom:
        - configMapRef:
            name: Khengleong-config
        - secretRef:
            name: Khengleong-secrets
        volumeMounts:
        - name: model-storage
          mountPath: /models
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 60
          periodSeconds: 30
      volumes:
      - name: model-storage
        persistentVolumeClaim:
          claimName: model-storage-pvc
---
apiVersion: v1
kind: Service
metadata:
  name: ai-extraction-service
  namespace: Khengleong
spec:
  selector:
    app: ai-extraction-service
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: ClusterIP
```

### 4.4 Ingress Configuration

```yaml
# k8s/ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: Khengleong-ingress
  namespace: Khengleong
  annotations:
    kubernetes.io/ingress.class: "nginx"
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/proxy-body-size: "50m"
    nginx.ingress.kubernetes.io/rate-limit: "100"
spec:
  tls:
  - hosts:
    - api.Khengleong.com
    - app.Khengleong.com
    secretName: Khengleong-tls
  rules:
  - host: api.Khengleong.com
    http:
      paths:
      - path: /api/v1/files
        pathType: Prefix
        backend:
          service:
            name: file-upload-service
            port:
              number: 80
      - path: /api/v1/extract
        pathType: Prefix
        backend:
          service:
            name: ai-extraction-service
            port:
              number: 80
      - path: /api/v1/templates
        pathType: Prefix
        backend:
          service:
            name: template-service
            port:
              number: 80
      - path: /api/v1/reports
        pathType: Prefix
        backend:
          service:
            name: report-service
            port:
              number: 80
      - path: /api/v1/auth
        pathType: Prefix
        backend:
          service:
            name: auth-service
            port:
              number: 80
  - host: app.Khengleong.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: frontend-service
            port:
              number: 80
```

### 4.5 Horizontal Pod Autoscaler

```yaml
# k8s/hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: file-upload-service-hpa
  namespace: Khengleong
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: file-upload-service
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: ai-extraction-service-hpa
  namespace: Khengleong
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: ai-extraction-service
  minReplicas: 2
  maxReplicas: 5
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 80
  - type: Resource
    resource:
      name: nvidia.com/gpu
      target:
        type: Utilization
        averageUtilization: 85
```

## 5. Database Setup

### 5.1 Database Initialization Script

```sql
-- database/init.sql
-- Create databases
CREATE DATABASE Khengleong;
CREATE DATABASE Khengleong_audit;

-- Create users
CREATE USER Khengleong_app WITH ENCRYPTED PASSWORD 'secure_password';
CREATE USER Khengleong_audit WITH ENCRYPTED PASSWORD 'secure_audit_password';

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE Khengleong TO Khengleong_app;
GRANT ALL PRIVILEGES ON DATABASE Khengleong_audit TO Khengleong_audit;

-- Connect to main database
\c Khengleong;

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "btree_gin";

-- Create schemas
CREATE SCHEMA IF NOT EXISTS app;
CREATE SCHEMA IF NOT EXISTS audit;

-- Grant schema permissions
GRANT ALL ON SCHEMA app TO Khengleong_app;
GRANT ALL ON SCHEMA audit TO Khengleong_audit;
```

### 5.2 Migration Management

```bash
#!/bin/bash
# scripts/migrate.sh

set -e

# Database connection parameters
DB_HOST=${DATABASE_HOST:-localhost}
DB_PORT=${DATABASE_PORT:-5432}
DB_NAME=${DATABASE_NAME:-Khengleong}
DB_USER=${DATABASE_USER:-Khengleong_app}
DB_PASSWORD=${DATABASE_PASSWORD}

# Migration directory
MIGRATION_DIR="./database/migrations"

# Function to run migration
run_migration() {
    local migration_file=$1
    local migration_name=$(basename "$migration_file" .sql)
    
    echo "Running migration: $migration_name"
    
    # Check if migration already applied
    if psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -t -c \
        "SELECT 1 FROM schema_migrations WHERE version = '$migration_name';" | grep -q 1; then
        echo "Migration $migration_name already applied, skipping..."
        return
    fi
    
    # Run migration
    psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -f "$migration_file"
    
    # Record migration
    psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -c \
        "INSERT INTO schema_migrations (version, description) VALUES ('$migration_name', 'Applied migration $migration_name');"
    
    echo "Migration $migration_name completed successfully"
}

# Run all pending migrations
for migration_file in $(ls $MIGRATION_DIR/*.sql | sort); do
    run_migration "$migration_file"
done

echo "All migrations completed successfully"
```

## 6. Security Configuration

### 6.1 Network Security

```yaml
# k8s/network-policy.yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: Khengleong-network-policy
  namespace: Khengleong
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: ingress-nginx
    - namespaceSelector:
        matchLabels:
          name: Khengleong
  egress:
  - to:
    - namespaceSelector:
        matchLabels:
          name: kube-system
  - to: []
    ports:
    - protocol: TCP
      port: 443  # HTTPS
    - protocol: TCP
      port: 53   # DNS
    - protocol: UDP
      port: 53   # DNS
```

### 6.2 Pod Security Standards

```yaml
# k8s/pod-security-policy.yaml
apiVersion: policy/v1beta1
kind: PodSecurityPolicy
metadata:
  name: Khengleong-psp
spec:
  privileged: false
  allowPrivilegeEscalation: false
  requiredDropCapabilities:
    - ALL
  volumes:
    - 'configMap'
    - 'emptyDir'
    - 'projected'
    - 'secret'
    - 'downwardAPI'
    - 'persistentVolumeClaim'
  runAsUser:
    rule: 'MustRunAsNonRoot'
  seLinux:
    rule: 'RunAsAny'
  fsGroup:
    rule: 'RunAsAny'
```

### 6.3 RBAC Configuration

```yaml
# k8s/rbac.yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: Khengleong-service-account
  namespace: Khengleong
---
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: Khengleong
  name: Khengleong-role
rules:
- apiGroups: [""]
  resources: ["pods", "services", "endpoints"]
  verbs: ["get", "list", "watch"]
- apiGroups: ["apps"]
  resources: ["deployments", "replicasets"]
  verbs: ["get", "list", "watch"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: Khengleong-role-binding
  namespace: Khengleong
subjects:
- kind: ServiceAccount
  name: Khengleong-service-account
  namespace: Khengleong
roleRef:
  kind: Role
  name: Khengleong-role
  apiGroup: rbac.authorization.k8s.io
```

## 7. Monitoring Setup

### 7.1 Prometheus Configuration

```yaml
# monitoring/prometheus-config.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: prometheus-config
  namespace: monitoring
data:
  prometheus.yml: |
    global:
      scrape_interval: 15s
      evaluation_interval: 15s

    rule_files:
      - "/etc/prometheus/rules/*.yml"

    scrape_configs:
      - job_name: 'kubernetes-pods'
        kubernetes_sd_configs:
          - role: pod
        relabel_configs:
          - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
            action: keep
            regex: true
          - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_path]
            action: replace
            target_label: __metrics_path__
            regex: (.+)

      - job_name: 'Khengleong-services'
        kubernetes_sd_configs:
          - role: endpoints
            namespaces:
              names:
                - Khengleong
        relabel_configs:
          - source_labels: [__meta_kubernetes_service_annotation_prometheus_io_scrape]
            action: keep
            regex: true
```

### 7.2 Grafana Dashboards

```json
{
  "dashboard": {
    "title": "Khengleong System Overview",
    "panels": [
      {
        "title": "Service Response Times",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket{job=~\"Khengleong.*\"}[5m])) by (le, service))",
            "legendFormat": "{{service}} 95th percentile"
          }
        ]
      },
      {
        "title": "Error Rates",
        "type": "graph",
        "targets": [
          {
            "expr": "sum(rate(http_requests_total{job=~\"Khengleong.*\",status=~\"5..\"}[5m])) by (service)",
            "legendFormat": "{{service}} errors"
          }
        ]
      },
      {
        "title": "Active Users",
        "type": "stat",
        "targets": [
          {
            "expr": "count(increase(user_login_total[5m]))",
            "legendFormat": "Active Users"
          }
        ]
      },
      {
        "title": "File Processing Queue",
        "type": "graph",
        "targets": [
          {
            "expr": "Khengleong_queue_size{queue=\"extraction\"}",
            "legendFormat": "Extraction Queue"
          }
        ]
      }
    ]
  }
}
```

### 7.3 Alerting Rules

```yaml
# monitoring/alert-rules.yaml
groups:
- name: Khengleong.rules
  rules:
  - alert: HighErrorRate
    expr: sum(rate(http_requests_total{status=~"5.."}[5m])) > 0.1
    for: 5m
    labels:
      severity: critical
    annotations:
      summary: "High error rate detected"
      description: "Error rate is {{ $value }} errors per second"

  - alert: ServiceDown
    expr: up{job=~"Khengleong.*"} == 0
    for: 1m
    labels:
      severity: critical
    annotations:
      summary: "Service {{ $labels.instance }} is down"

  - alert: HighMemoryUsage
    expr: (container_memory_usage_bytes / container_spec_memory_limit_bytes) > 0.8
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "High memory usage on {{ $labels.instance }}"

  - alert: DatabaseConnectionsHigh
    expr: postgresql_connections_total > 80
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "High number of database connections"
```

## 8. CI/CD Pipeline

### 8.1 GitHub Actions Workflow

```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: Khengleong

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Setup Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '18'
        cache: 'npm'
    
    - name: Install dependencies
      run: npm ci
    
    - name: Run tests
      run: npm run test:coverage
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3

  build:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    strategy:
      matrix:
        service: [file-upload, ai-extraction, template, report, auth, frontend]
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Log in to Container Registry
      uses: docker/login-action@v2
      with:
        registry: ${{ env.REGISTRY }}
        username: ${{ github.actor }}
        password: ${{ secrets.GITHUB_TOKEN }}
    
    - name: Build and push Docker image
      uses: docker/build-push-action@v3
      with:
        context: ./services/${{ matrix.service }}
        push: true
        tags: |
          ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}/${{ matrix.service }}:latest
          ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}/${{ matrix.service }}:${{ github.sha }}

  deploy:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Configure AWS credentials
      uses: aws-actions/configure-aws-credentials@v2
      with:
        aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
        aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        aws-region: us-west-2
    
    - name: Update kubeconfig
      run: aws eks update-kubeconfig --region us-west-2 --name Khengleong-cluster
    
    - name: Deploy to Kubernetes
      run: |
        # Update image tags in deployment files
        sed -i "s|:latest|:${{ github.sha }}|g" k8s/*.yaml
        
        # Apply configurations
        kubectl apply -f k8s/ -n Khengleong
        
        # Wait for deployment rollout
        kubectl rollout status deployment/file-upload-service -n Khengleong
        kubectl rollout status deployment/ai-extraction-service -n Khengleong
        kubectl rollout status deployment/template-service -n Khengleong
        kubectl rollout status deployment/report-service -n Khengleong
        kubectl rollout status deployment/auth-service -n Khengleong
        kubectl rollout status deployment/frontend -n Khengleong
    
    - name: Run smoke tests
      run: |
        # Wait for services to be ready
        kubectl wait --for=condition=ready pod -l app=file-upload-service -n Khengleong --timeout=300s
        
        # Run smoke tests
        npm run test:smoke
```

### 8.2 Deployment Scripts

```bash
#!/bin/bash
# scripts/deploy.sh

set -e

# Configuration
ENVIRONMENT=${1:-staging}
NAMESPACE="Khengleong-${ENVIRONMENT}"
IMAGE_TAG=${2:-latest}

echo "Deploying Khengleong to ${ENVIRONMENT} environment..."

# Validate kubectl context
CURRENT_CONTEXT=$(kubectl config current-context)
echo "Current kubectl context: ${CURRENT_CONTEXT}"

# Create namespace if it doesn't exist
kubectl create namespace ${NAMESPACE} --dry-run=client -o yaml | kubectl apply -f -

# Apply configurations
echo "Applying configurations..."
envsubst < k8s/configmap.yaml | kubectl apply -f - -n ${NAMESPACE}
kubectl apply -f k8s/secrets.yaml -n ${NAMESPACE}

# Deploy services
echo "Deploying services..."
for service in file-upload-service ai-extraction-service template-service report-service auth-service frontend; do
    echo "Deploying ${service}..."
    envsubst < k8s/${service}.yaml | kubectl apply -f - -n ${NAMESPACE}
    kubectl rollout status deployment/${service} -n ${NAMESPACE} --timeout=600s
done

# Apply ingress and networking
kubectl apply -f k8s/ingress.yaml -n ${NAMESPACE}
kubectl apply -f k8s/network-policy.yaml -n ${NAMESPACE}

# Run health checks
echo "Running health checks..."
./scripts/health-check.sh ${NAMESPACE}

echo "Deployment completed successfully!"
```

## 9. Backup and Recovery

### 9.1 Database Backup Strategy

```bash
#!/bin/bash
# scripts/backup-database.sh

set -e

# Configuration
BACKUP_DIR="/backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
RETENTION_DAYS=30

# Database connection
DB_HOST=${DATABASE_HOST}
DB_PORT=${DATABASE_PORT:-5432}
DB_NAME=${DATABASE_NAME}
DB_USER=${DATABASE_USER}

# Create backup directory
mkdir -p ${BACKUP_DIR}

# Full database backup
echo "Creating full database backup..."
pg_dump -h ${DB_HOST} -p ${DB_PORT} -U ${DB_USER} -d ${DB_NAME} \
    -f ${BACKUP_DIR}/Khengleong_full_${TIMESTAMP}.sql

# Compress backup
gzip ${BACKUP_DIR}/Khengleong_full_${TIMESTAMP}.sql

# Upload to S3
aws s3 cp ${BACKUP_DIR}/Khengleong_full_${TIMESTAMP}.sql.gz \
    s3://Khengleong-backups/database/full/

# Schema-only backup
echo "Creating schema backup..."
pg_dump -h ${DB_HOST} -p ${DB_PORT} -U ${DB_USER} -d ${DB_NAME} \
    --schema-only -f ${BACKUP_DIR}/Khengleong_schema_${TIMESTAMP}.sql

# Upload schema backup
aws s3 cp ${BACKUP_DIR}/Khengleong_schema_${TIMESTAMP}.sql \
    s3://Khengleong-backups/database/schema/

# Clean up old backups
find ${BACKUP_DIR} -name "Khengleong_*" -mtime +${RETENTION_DAYS} -delete

# Clean up old S3 backups
aws s3 ls s3://Khengleong-backups/database/full/ \
    | awk '{print $4}' \
    | head -n -${RETENTION_DAYS} \
    | xargs -I {} aws s3 rm s3://Khengleong-backups/database/full/{}

echo "Database backup completed successfully"
```

### 9.2 Application Data Backup

```bash
#!/bin/bash
# scripts/backup-files.sh

set -e

# Configuration
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
S3_BUCKET="Khengleong-file-backups"

# Backup uploaded files
echo "Backing up uploaded files..."
aws s3 sync s3://Khengleong-files/uploads/ \
    s3://${S3_BUCKET}/files/${TIMESTAMP}/uploads/ \
    --storage-class STANDARD_IA

# Backup templates
echo "Backing up templates..."
aws s3 sync s3://Khengleong-files/templates/ \
    s3://${S3_BUCKET}/files/${TIMESTAMP}/templates/ \
    --storage-class STANDARD_IA

# Backup generated reports
echo "Backing up reports..."
aws s3 sync s3://Khengleong-files/reports/ \
    s3://${S3_BUCKET}/files/${TIMESTAMP}/reports/ \
    --storage-class STANDARD_IA

echo "File backup completed successfully"
```

### 9.3 Disaster Recovery Procedure

```bash
#!/bin/bash
# scripts/disaster-recovery.sh

set -e

# Configuration
RECOVERY_POINT=${1:-latest}
NEW_REGION=${2:-us-east-1}

echo "Starting disaster recovery procedure..."
echo "Recovery point: ${RECOVERY_POINT}"
echo "Target region: ${NEW_REGION}"

# 1. Setup new infrastructure
echo "Setting up infrastructure in ${NEW_REGION}..."
cd terraform/
terraform workspace select disaster-recovery || terraform workspace new disaster-recovery
terraform init
terraform apply -var="region=${NEW_REGION}" -auto-approve

# 2. Restore database
echo "Restoring database..."
if [ "${RECOVERY_POINT}" = "latest" ]; then
    BACKUP_FILE=$(aws s3 ls s3://Khengleong-backups/database/full/ | sort | tail -n 1 | awk '{print $4}')
else
    BACKUP_FILE="${RECOVERY_POINT}"
fi

aws s3 cp s3://Khengleong-backups/database/full/${BACKUP_FILE} /tmp/
gunzip /tmp/${BACKUP_FILE}
psql -h ${NEW_DB_HOST} -U ${DB_USER} -d ${DB_NAME} -f /tmp/${BACKUP_FILE%.gz}

# 3. Restore file data
echo "Restoring file data..."
aws s3 sync s3://Khengleong-file-backups/files/${RECOVERY_POINT}/ \
    s3://Khengleong-files-${NEW_REGION}/

# 4. Deploy applications
echo "Deploying applications..."
kubectl config use-context ${NEW_REGION}
./scripts/deploy.sh production

# 5. Update DNS
echo "Updating DNS records..."
# This would typically involve updating Route 53 or your DNS provider
# to point to the new infrastructure

echo "Disaster recovery completed successfully"
echo "New endpoint: https://api-${NEW_REGION}.Khengleong.com"
```

## 10. Troubleshooting

### 10.1 Common Issues and Solutions

#### Pod Startup Issues
```bash
# Check pod status
kubectl get pods -n Khengleong

# Check pod logs
kubectl logs -f deployment/file-upload-service -n Khengleong

# Describe pod for events
kubectl describe pod <pod-name> -n Khengleong

# Check resource usage
kubectl top pods -n Khengleong
```

#### Database Connection Issues
```bash
# Test database connectivity
kubectl run -it --rm debug --image=postgres:14 --restart=Never -- \
    psql -h Khengleong-db.cluster-xyz.region.rds.amazonaws.com -U Khengleong -d Khengleong

# Check database logs
aws rds describe-db-log-files --db-instance-identifier Khengleong-db
aws rds download-db-log-file-portion --db-instance-identifier Khengleong-db \
    --log-file-name error/postgresql.log.2025-01-30-10
```

#### Performance Issues
```bash
# Check service metrics
kubectl get --raw /metrics | grep Khengleong

# Monitor resource usage
kubectl top nodes
kubectl top pods -n Khengleong

# Check HPA status
kubectl get hpa -n Khengleong
kubectl describe hpa file-upload-service-hpa -n Khengleong
```

### 10.2 Emergency Procedures

#### Service Restart
```bash
#!/bin/bash
# Emergency service restart
SERVICE_NAME=${1}
NAMESPACE=${2:-Khengleong}

echo "Restarting ${SERVICE_NAME} in ${NAMESPACE}..."
kubectl rollout restart deployment/${SERVICE_NAME} -n ${NAMESPACE}
kubectl rollout status deployment/${SERVICE_NAME} -n ${NAMESPACE}
```

#### Scale Down for Maintenance
```bash
#!/bin/bash
# Scale down all services for maintenance
NAMESPACE=${1:-Khengleong}

echo "Scaling down services for maintenance..."
kubectl scale deployment --all --replicas=0 -n ${NAMESPACE}

# Wait for pods to terminate
kubectl wait --for=delete pod --all -n ${NAMESPACE} --timeout=300s

echo "All services scaled down. Maintenance window is now active."
```

#### Emergency Rollback
```bash
#!/bin/bash
# Emergency rollback to previous version
SERVICE_NAME=${1}
NAMESPACE=${2:-Khengleong}

echo "Rolling back ${SERVICE_NAME}..."
kubectl rollout undo deployment/${SERVICE_NAME} -n ${NAMESPACE}
kubectl rollout status deployment/${SERVICE_NAME} -n ${NAMESPACE}

echo "Rollback completed successfully"
```

---

*Document Version: 1.0*  
*Last Updated: 2025-01-30*  
*Author: DevOps Team*
# JAH Agency Environment Configuration Template
# =============================================
#
# Copy this file to .env and fill in your actual values.
# Never commit the .env file to version control!
#
# Usage:
#   cp .env.example .env
#   # Edit .env with your actual values
#   # The application will automatically load these variables
#
# Categories:
#   🏗️  System Configuration
#   🗄️  Database Configuration  
#   🔐 Security & Authentication
#   🤖 AI & Machine Learning APIs
#   💰 Financial & Payment APIs
#   📊 Freelancing Platform APIs
#   📧 Communication Services
#   📈 Monitoring & Analytics
#   🐳 Docker & Deployment
#   🔧 Development & Testing

# ===================
# 🏗️ SYSTEM CONFIGURATION
# ===================

# Environment: development, staging, production
ENVIRONMENT=development

# Application settings
DEBUG_MODE=true
LOG_LEVEL=INFO
TIMEZONE=UTC
OPERATION_CYCLE=60

# Application ports
APP_PORT=8000
METRICS_PORT=8090

# Python version for Docker builds
PYTHON_VERSION=3.11
BUILD_TARGET=development

# ===================
# 🗄️ DATABASE CONFIGURATION
# ===================

# PostgreSQL (Primary Database)
DB_TYPE=postgresql
DB_HOST=localhost
DB_PORT=5432
DB_NAME=jah_agency
DB_USERNAME=jah_user
DB_PASSWORD=your_secure_db_password_here
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=30
DB_POOL_TIMEOUT=30
DB_SSL_MODE=prefer

# Redis (Caching & Message Queue)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_DB=0
REDIS_MAX_CONNECTIONS=50
REDIS_SOCKET_TIMEOUT=30

# MongoDB (Document Storage - Optional)
MONGODB_ENABLED=false
MONGODB_URI=mongodb://localhost:27017
MONGODB_DATABASE=jah_agency_docs
MONGO_USERNAME=mongo_user
MONGO_PASSWORD=your_mongo_password_here
MONGO_PORT=27017

# ===================
# 🔐 SECURITY & AUTHENTICATION
# ===================

# Encryption & JWT
MASTER_ENCRYPTION_KEY=your-32-character-master-key-here
JWT_SECRET=your-super-secret-jwt-key-change-this
JWT_EXPIRATION=24

# API Security
RATE_LIMIT=100
CORS_ORIGINS=http://localhost:3000,http://localhost:8080

# Authentication
AUTH_METHOD=jwt
OAUTH2_PROVIDER=
OAUTH2_CLIENT_ID=
OAUTH2_CLIENT_SECRET=

# Admin Access
ADMIN_USERS=admin@jahagency.com
READONLY_USERS=

# ===================
# 🤖 AI & MACHINE LEARNING APIS
# ===================

# OpenAI (Primary AI Provider)
OPENAI_API_KEY=sk-your-openai-api-key-here
OPENAI_ORG_ID=org-your-organization-id-here

# Anthropic (Claude API)
ANTHROPIC_API_KEY=sk-ant-your-anthropic-api-key-here

# Agent Model Configuration
PRIMARY_AGENT_MODEL=gpt-4-turbo
MARKETING_AGENT_MODEL=gpt-4
SALES_AGENT_MODEL=gpt-4
TECHNICAL_AGENT_MODEL=gpt-4-turbo
RESEARCH_AGENT_MODEL=gpt-4
CUSTOMER_SERVICE_MODEL=gpt-3.5-turbo

# ===================
# 💰 FINANCIAL & PAYMENT APIS
# ===================

# Stripe (Primary Payment Processor)
STRIPE_ENABLED=true
STRIPE_PUBLIC_KEY=pk_test_your_stripe_public_key_here
STRIPE_SECRET_KEY=sk_test_your_stripe_secret_key_here
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret_here

# PayPal (Alternative Payment Processor)
PAYPAL_ENABLED=false
PAYPAL_CLIENT_ID=your_paypal_client_id_here
PAYPAL_CLIENT_SECRET=your_paypal_client_secret_here
PAYPAL_ENV=sandbox

# Cryptocurrency Payments (Optional)
CRYPTO_PAYMENTS_ENABLED=false

# Banking & Financial APIs
PRIMARY_BANK=
PRIMARY_ACCOUNT=
PRIMARY_ROUTING=
OPERATIONAL_BANK=
OPERATIONAL_ACCOUNT=
OPERATIONAL_ROUTING=

# Financial Reporting
FINANCIAL_REPORT_EMAIL=admin@jahagency.com

# ===================
# 📊 FREELANCING PLATFORM APIS
# ===================

# Upwork Integration
UPWORK_ENABLED=true
UPWORK_API_KEY=your_upwork_api_key_here
UPWORK_SECRET_KEY=your_upwork_secret_key_here
AUTO_BIDDING_ENABLED=true

# Freelancer.com Integration
FREELANCER_ENABLED=true
FREELANCER_API_KEY=your_freelancer_api_key_here
FREELANCER_SECRET_KEY=your_freelancer_secret_key_here

# Fiverr Integration
FIVERR_ENABLED=false
FIVERR_API_KEY=your_fiverr_api_key_here

# Service Pricing
WEB_DEV_RATE=75
DATA_ANALYSIS_RATE=85
CONTENT_RATE=45
AUTOMATION_RATE=95

# Market Scanning
MARKET_SCAN_FREQUENCY=300

# ===================
# 📧 COMMUNICATION SERVICES
# ===================

# Email Configuration
EMAIL_ENABLED=true
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
EMAIL_USERNAME=your_email@gmail.com
EMAIL_PASSWORD=your_app_password_here
EMAIL_FROM=noreply@jahagency.com

# Slack Integration
SLACK_ENABLED=false
SLACK_BOT_TOKEN=xoxb-your-slack-bot-token-here
SLACK_CHANNEL=#jah-agency

# Discord Integration
DISCORD_ENABLED=false
DISCORD_BOT_TOKEN=your_discord_bot_token_here
DISCORD_GUILD_ID=your_discord_guild_id_here

# Twilio (SMS/Phone)
TWILIO_ENABLED=false
TWILIO_ACCOUNT_SID=your_twilio_account_sid_here
TWILIO_AUTH_TOKEN=your_twilio_auth_token_here
TWILIO_PHONE_NUMBER=+1234567890

# SendGrid (Email Service)
SENDGRID_ENABLED=false
SENDGRID_API_KEY=SG.your_sendgrid_api_key_here

# Webhook URLs
FINANCIAL_WEBHOOK_URL=https://your-domain.com/webhooks/financial
TASK_WEBHOOK_URL=https://your-domain.com/webhooks/tasks

# ===================
# 📈 MONITORING & ANALYTICS
# ===================

# Prometheus Metrics
PROMETHEUS_ENABLED=true
PROMETHEUS_PORT=9090

# Distributed Tracing
TRACING_ENABLED=false
JAEGER_ENDPOINT=http://localhost:14268
JAEGER_UI_PORT=16686
JAEGER_COLLECTOR_PORT=14268

# Error Tracking
SENTRY_ENABLED=false
SENTRY_DSN=https://your-sentry-dsn-here

# Google Analytics
GA_ENABLED=false
GA_TRACKING_ID=UA-your-tracking-id-here
GA_SERVICE_ACCOUNT_KEY=

# Business Intelligence
CRUNCHBASE_ENABLED=false
CRUNCHBASE_API_KEY=your_crunchbase_api_key_here

# Application Performance Monitoring
NEWRELIC_ENABLED=false
NEW_RELIC_LICENSE_KEY=your_newrelic_license_key_here

# ===================
# 🐳 DOCKER & DEPLOYMENT
# ===================

# Docker Compose Ports
HTTP_PORT=80
HTTPS_PORT=443
GRAFANA_PORT=3000
FLOWER_PORT=5555
PGADMIN_PORT=8080
REDIS_COMMANDER_PORT=8081
MAILHOG_WEB_PORT=8025
MAILHOG_SMTP_PORT=1025

# Admin Tool Credentials
GRAFANA_PASSWORD=admin123
PGADMIN_EMAIL=admin@jahagency.com
PGADMIN_PASSWORD=admin123
REDIS_COMMANDER_USER=admin
REDIS_COMMANDER_PASSWORD=admin123

# Container Resource Limits
CONTAINER_MEMORY_LIMIT=2g
CONTAINER_CPU_LIMIT=1.0

# ===================
# ☁️ CLOUD STORAGE & BACKUP
# ===================

# Backup Configuration
BACKUP_STORAGE_TYPE=local
BACKUP_PATH=/backups

# AWS S3 (for backups and file storage)
AWS_ACCESS_KEY=your_aws_access_key_here
AWS_SECRET_KEY=your_aws_secret_key_here
AWS_REGION=us-east-1
S3_BACKUP_BUCKET=jah-agency-backups

# Google Cloud Storage
GCS_ENABLED=false
GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account-key.json
GCS_BUCKET_NAME=jah-agency-storage

# Azure Blob Storage
AZURE_ENABLED=false
AZURE_STORAGE_ACCOUNT=your_storage_account_here
AZURE_STORAGE_KEY=your_storage_key_here
AZURE_CONTAINER_NAME=jah-agency-container

# ===================
# 🔧 DEVELOPMENT & TESTING
# ===================

# Development Settings
HOT_RELOAD=false
MOCK_APIS=false

# Testing Configuration
TEST_DATABASE_URL=postgresql://test_user:test_pass@localhost:5433/test_jah_agency
COVERAGE_THRESHOLD=80
PARALLEL_TESTS=true

# Feature Flags
FEATURE_AUTO_BIDDING=true
FEATURE_AI_PROPOSALS=true
FEATURE_PREDICTIVE=true
FEATURE_MULTILANG=false
FEATURE_BLOCKCHAIN=false
FEATURE_ADVANCED_ML=true

# Debug Tools
FLASK_DEBUG=false
DJANGO_DEBUG=false
FASTAPI_DEBUG=false

# ===================
# 🌐 EXTERNAL INTEGRATIONS
# ===================

# Social Media APIs
TWITTER_API_KEY=your_twitter_api_key_here
TWITTER_API_SECRET=your_twitter_api_secret_here
TWITTER_ACCESS_TOKEN=your_twitter_access_token_here
TWITTER_ACCESS_TOKEN_SECRET=your_twitter_access_token_secret_here

FACEBOOK_APP_ID=your_facebook_app_id_here
FACEBOOK_APP_SECRET=your_facebook_app_secret_here

LINKEDIN_CLIENT_ID=your_linkedin_client_id_here
LINKEDIN_CLIENT_SECRET=your_linkedin_client_secret_here

# CRM Integration
SALESFORCE_ENABLED=false
SALESFORCE_CLIENT_ID=your_salesforce_client_id_here
SALESFORCE_CLIENT_SECRET=your_salesforce_client_secret_here

HUBSPOT_ENABLED=false
HUBSPOT_API_KEY=your_hubspot_api_key_here

# Project Management
ASANA_ENABLED=false
ASANA_ACCESS_TOKEN=your_asana_access_token_here

TRELLO_ENABLED=false
TRELLO_API_KEY=your_trello_api_key_here
TRELLO_TOKEN=your_trello_token_here

JIRA_ENABLED=false
JIRA_URL=https://your-domain.atlassian.net
JIRA_USERNAME=your_jira_username_here
JIRA_API_TOKEN=your_jira_api_token_here

# ===================
# 📊 BUSINESS INTELLIGENCE
# ===================

# Analytics & Reporting
MIXPANEL_ENABLED=false
MIXPANEL_TOKEN=your_mixpanel_token_here

AMPLITUDE_ENABLED=false
AMPLITUDE_API_KEY=your_amplitude_api_key_here

# Market Data
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_api_key_here
YAHOO_FINANCE_ENABLED=true

# Competitor Analysis
SIMILARWEB_API_KEY=your_similarweb_api_key_here
SEMRUSH_API_KEY=your_semrush_api_key_here

# ===================
# 🔒 SECURITY & COMPLIANCE
# ===================

# SSL/TLS Configuration
SSL_ENABLED=false
SSL_CERT_PATH=/etc/ssl/certs/cert.pem
SSL_KEY_PATH=/etc/ssl/private/key.pem

# Rate Limiting
RATE_LIMIT_REDIS_URL=redis://localhost:6379
RATE_LIMIT_STORAGE_URL=redis://localhost:6379

# Session Security
SESSION_SECRET_KEY=your-session-secret-key-here
SESSION_TIMEOUT=3600

# GDPR Compliance
GDPR_ENABLED=false
DATA_RETENTION_DAYS=365
COOKIE_CONSENT_REQUIRED=false

# Security Headers
SECURITY_HEADERS_ENABLED=true
CONTENT_SECURITY_POLICY_ENABLED=true

# ===================
# 🚀 PERFORMANCE OPTIMIZATION
# ===================

# Caching Configuration
CACHE_TYPE=redis
CACHE_DEFAULT_TIMEOUT=300
CACHE_KEY_PREFIX=jah_agency

# Database Connection Pooling
DB_POOL_PRE_PING=true
DB_POOL_RECYCLE=3600
DB_ECHO=false

# Background Tasks
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
CELERY_WORKER_CONCURRENCY=4
CELERY_TASK_SERIALIZER=json
CELERY_RESULT_SERIALIZER=json

# Content Delivery Network
CDN_ENABLED=false
CDN_URL=https://cdn.jahagency.com

# ===================
# 📝 LOGGING & AUDITING
# ===================

# Logging Configuration
LOG_FORMAT=%(asctime)s - %(name)s - %(levelname)s - %(message)s
LOG_MAX_BYTES=10485760
LOG_BACKUP_COUNT=5

# Audit Logging
AUDIT_ENABLED=true
AUDIT_LOG_LEVEL=INFO
AUDIT_RETENTION_DAYS=365

# External Logging Services
PAPERTRAIL_ENABLED=false
PAPERTRAIL_HOST=logs.papertrailapp.com
PAPERTRAIL_PORT=12345

LOGSTASH_ENABLED=false
LOGSTASH_HOST=localhost
LOGSTASH_PORT=5044

# ===================
# 🔄 BACKUP & RECOVERY
# ===================

# Automated Backups
BACKUP_ENABLED=true
BACKUP_SCHEDULE=0 2 * * *
BACKUP_RETENTION_DAYS=30
BACKUP_COMPRESSION=true

# Database Backup
DB_BACKUP_ENABLED=true
DB_BACKUP_FORMAT=custom

# File Backup
FILE_BACKUP_ENABLED=true
FILE_BACKUP_EXCLUDE=*.log,*.tmp,__pycache__

# Recovery Configuration
RECOVERY_POINT_OBJECTIVE=1440  # minutes
RECOVERY_TIME_OBJECTIVE=60     # minutes

# ===================
# 🌍 LOCALIZATION & INTERNATIONALIZATION
# ===================

# Language Settings
DEFAULT_LANGUAGE=en
SUPPORTED_LANGUAGES=en,es,fr,de,zh,ja
TIMEZONE_DETECTION=true

# Currency Settings
DEFAULT_CURRENCY=USD
SUPPORTED_CURRENCIES=USD,EUR,GBP,JPY,CAD,AUD

# Regional Settings
DEFAULT_COUNTRY=US
TAX_CALCULATION_ENABLED=false

# ===================
# 📱 MOBILE & API CONFIGURATION
# ===================

# Mobile App Settings
MOBILE_API_ENABLED=true
MOBILE_API_VERSION=v1
PUSH_NOTIFICATIONS_ENABLED=false

# Firebase (for mobile push notifications)
FIREBASE_ENABLED=false
FIREBASE_SERVER_KEY=your_firebase_server_key_here
FIREBASE_PROJECT_ID=your_firebase_project_id_here

# API Versioning
API_VERSION=v2
API_DEPRECATION_WARNINGS=true

# ===================
# 🧪 A/B TESTING & EXPERIMENTS
# ===================

# Feature Experiments
EXPERIMENTS_ENABLED=false
EXPERIMENT_FRAMEWORK=internal

# Split Testing
SPLIT_IO_ENABLED=false
SPLIT_IO_API_KEY=your_split_io_api_key_here

# ===================
# ⚡ REAL-TIME FEATURES
# ===================

# WebSocket Configuration
WEBSOCKET_ENABLED=true
WEBSOCKET_MAX_CONNECTIONS=1000
WEBSOCKET_HEARTBEAT_INTERVAL=30

# Real-time Notifications
REALTIME_NOTIFICATIONS=true
NOTIFICATION_CHANNELS=websocket,email,slack

# ===================
# 🔍 SEARCH & INDEXING
# ===================

# Elasticsearch (Optional)
ELASTICSEARCH_ENABLED=false
ELASTICSEARCH_URL=http://localhost:9200
ELASTICSEARCH_INDEX=jah_agency

# Full-text Search
SEARCH_ENABLED=true
SEARCH_PROVIDER=database

# ===================
# 🎨 FRONTEND & UI
# ===================

# Frontend Framework
FRONTEND_ENABLED=false
FRONTEND_URL=http://localhost:3000

# Theme & Branding
THEME=default
BRAND_NAME=JAH Agency
BRAND_COLOR=#007bff
LOGO_URL=/static/logo.png

# ===================
# 📞 SUPPORT & HELPDESK
# ===================

# Customer Support
SUPPORT_EMAIL=support@jahagency.com
SUPPORT_PHONE=+1-555-0123
SUPPORT_HOURS=9:00-17:00 UTC

# Help Desk Integration
ZENDESK_ENABLED=false
ZENDESK_SUBDOMAIN=your_subdomain
ZENDESK_USERNAME=your_zendesk_username
ZENDESK_TOKEN=your_zendesk_token

INTERCOM_ENABLED=false
INTERCOM_APP_ID=your_intercom_app_id_here

# ===================
# 🏢 ENTERPRISE FEATURES
# ===================

# Single Sign-On (SSO)
SSO_ENABLED=false
SAML_ENABLED=false
SAML_IDP_URL=
SAML_CERTIFICATE=

# Multi-tenancy
MULTI_TENANT=false
TENANT_ISOLATION=database

# Enterprise Integrations
ACTIVE_DIRECTORY_ENABLED=false
LDAP_ENABLED=false

# Compliance & Governance
SOX_COMPLIANCE=false
HIPAA_COMPLIANCE=false
SOC2_COMPLIANCE=false

# ===================
# 🔧 MAINTENANCE & OPERATIONS
# ===================

# Maintenance Windows
MAINTENANCE_MODE=false
MAINTENANCE_MESSAGE=System is under maintenance. Please try again later.

# Health Checks
HEALTH_CHECK_ENABLED=true
HEALTH_CHECK_INTERVAL=30
HEALTH_CHECK_TIMEOUT=10

# System Limits
MAX_REQUEST_SIZE=100MB
MAX_UPLOAD_SIZE=50MB
MAX_CONCURRENT_REQUESTS=1000

# Auto-scaling
AUTO_SCALING_ENABLED=false
MIN_INSTANCES=1
MAX_INSTANCES=10
SCALE_UP_THRESHOLD=80
SCALE_DOWN_THRESHOLD=30
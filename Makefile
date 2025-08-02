.PHONY: help build up down logs clean restart dev prod backup restore

# Default target
help:
	@echo "🤖 ZipHostBot - Makefile Commands"
	@echo ""
	@echo "Development:"
	@echo "  make setup    - Setup environment dan dependencies"
	@echo "  make dev      - Jalankan dalam mode development"
	@echo "  make build    - Build semua Docker images"
	@echo "  make up       - Start semua services"
	@echo "  make down     - Stop semua services"
	@echo "  make restart  - Restart semua services"
	@echo ""
	@echo "Monitoring:"
	@echo "  make logs     - Lihat logs semua services"
	@echo "  make status   - Lihat status containers"
	@echo ""
	@echo "Maintenance:"
	@echo "  make clean    - Cleanup containers dan images"
	@echo "  make backup   - Backup database"
	@echo "  make restore  - Restore database dari backup"
	@echo ""
	@echo "Examples:"
	@echo "  make examples - Buat contoh bot ZIP files"
	@echo ""
	@echo "Production:"
	@echo "  make prod     - Deploy untuk production"

# Setup environment
setup:
	@echo "🔧 Setting up ZipHostBot..."
	@if [ ! -f .env ]; then \
		echo "📋 Copying .env.example to .env..."; \
		cp .env.example .env; \
		echo "⚠️  Please edit .env file with your configuration!"; \
	else \
		echo "✅ .env file already exists"; \
	fi
	@echo "🚀 Run 'make dev' to start development environment"

# Development mode
dev: setup
	@echo "🚀 Starting ZipHostBot in development mode..."
	docker-compose up --build

# Build images
build:
	@echo "🔨 Building Docker images..."
	docker-compose build

# Start services
up:
	@echo "▶️  Starting ZipHostBot services..."
	docker-compose up -d

# Stop services
down:
	@echo "⏹️  Stopping ZipHostBot services..."
	docker-compose down

# Restart services
restart: down up
	@echo "🔄 ZipHostBot services restarted"

# View logs
logs:
	@echo "📋 Viewing logs..."
	docker-compose logs -f

# View specific service logs
logs-backend:
	docker-compose logs -f backend

logs-worker:
	docker-compose logs -f worker

logs-frontend:
	docker-compose logs -f frontend

logs-db:
	docker-compose logs -f db

# Check status
status:
	@echo "📊 Container status:"
	docker-compose ps

# Clean up
clean:
	@echo "🧹 Cleaning up..."
	docker-compose down -v
	docker system prune -f
	docker volume prune -f

# Clean everything (DANGEROUS!)
clean-all:
	@echo "⚠️  This will remove ALL Docker data!"
	@read -p "Are you sure? (y/N): " confirm && [ "$$confirm" = "y" ]
	docker-compose down -v
	docker system prune -af
	docker volume prune -f

# Database backup
backup:
	@echo "💾 Creating database backup..."
	@mkdir -p backups
	docker-compose exec db pg_dump -U zippy ziphostbot_db > backups/backup_$(shell date +%Y%m%d_%H%M%S).sql
	@echo "✅ Backup created in backups/ directory"

# Database restore
restore:
	@echo "📥 Available backups:"
	@ls -la backups/*.sql 2>/dev/null || echo "No backups found"
	@echo ""
	@read -p "Enter backup filename: " backup_file; \
	if [ -f "backups/$$backup_file" ]; then \
		echo "🔄 Restoring database from $$backup_file..."; \
		docker-compose exec -T db psql -U zippy ziphostbot_db < "backups/$$backup_file"; \
		echo "✅ Database restored successfully"; \
	else \
		echo "❌ Backup file not found"; \
	fi

# Create example bot ZIP files
examples:
	@echo "📦 Creating example bot ZIP files..."
	cd examples && ./create-zip.sh python
	cd examples && ./create-zip.sh nodejs
	@echo "✅ Example ZIP files created!"

# Production deployment
prod:
	@echo "🚀 Deploying to production..."
	@if [ ! -f .env ]; then \
		echo "❌ .env file not found! Run 'make setup' first."; \
		exit 1; \
	fi
	docker-compose -f docker-compose.yml up -d --build
	@echo "✅ Production deployment complete!"

# Update system
update:
	@echo "🔄 Updating ZipHostBot..."
	git pull
	docker-compose build --no-cache
	docker-compose up -d
	@echo "✅ Update complete!"

# Show environment info
info:
	@echo "ℹ️  ZipHostBot Environment Info:"
	@echo "Docker version: $(shell docker --version)"
	@echo "Docker Compose version: $(shell docker-compose --version)"
	@echo "Current directory: $(shell pwd)"
	@echo "Git branch: $(shell git branch --show-current 2>/dev/null || echo 'Not a git repository')"
	@echo "Services status:"
	@docker-compose ps 2>/dev/null || echo "Services not running"

# Health check
health:
	@echo "🏥 Health check..."
	@curl -f http://localhost/health 2>/dev/null && echo "✅ Frontend healthy" || echo "❌ Frontend unhealthy"
	@curl -f http://localhost/api/ 2>/dev/null && echo "✅ Backend healthy" || echo "❌ Backend unhealthy"

# Install development dependencies
install-dev:
	@echo "📦 Installing development dependencies..."
	cd frontend && npm install
	cd backend && pip install -r requirements.txt
	cd worker && pip install -r requirements.txt

# Run tests (placeholder)
test:
	@echo "🧪 Running tests..."
	@echo "⚠️  Tests not implemented yet"

# Generate secrets
secrets:
	@echo "🔐 Generating secrets..."
	@echo "JWT_SECRET=$(shell openssl rand -hex 32)"
	@echo "ENCRYPTION_KEY=$(shell openssl rand -hex 32)"
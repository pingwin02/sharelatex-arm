# Makefile

MONOREPO_ROOT := ../
export OVERLEAF_BASE_TAG ?= pingwin02/sharelatex-arm:base
export OVERLEAF_SLIM_TAG ?= pingwin02/sharelatex-arm:slim
export OVERLEAF_FULL_TAG ?= pingwin02/sharelatex-arm:full
export OVERLEAF_LATEST_TAG ?= pingwin02/sharelatex-arm:latest

DATE = $(shell date +%Y-%m-%d)

all: build-base build-slim build-full push

build-base:
	cp .dockerignore $(MONOREPO_ROOT)
	docker build \
	  --build-arg BUILDKIT_INLINE_CACHE=1 \
	  --file Dockerfile-base \
	  --tag $(OVERLEAF_BASE_TAG) \
	  --tag $(OVERLEAF_BASE_TAG)-$(DATE) \
	  $(MONOREPO_ROOT)

build-slim:
	cp .dockerignore $(MONOREPO_ROOT)
	docker build \
	  --build-arg BUILDKIT_INLINE_CACHE=1 \
	  --file Dockerfile \
	  --tag $(OVERLEAF_SLIM_TAG) \
	  --tag $(OVERLEAF_SLIM_TAG)-$(DATE) \
	  $(MONOREPO_ROOT)

build-full:
	cp .dockerignore $(MONOREPO_ROOT)
	docker build \
	  --build-arg BUILDKIT_INLINE_CACHE=1 \
	  --file Dockerfile-full \
	  --tag $(OVERLEAF_FULL_TAG) \
	  --tag $(OVERLEAF_LATEST_TAG) \
	  --tag $(OVERLEAF_FULL_TAG)-$(DATE) \
	  $(MONOREPO_ROOT)

push:
	docker push $(OVERLEAF_BASE_TAG)-$(DATE)
	docker push $(OVERLEAF_SLIM_TAG)-$(DATE)
	docker push $(OVERLEAF_FULL_TAG)-$(DATE)
	docker push $(OVERLEAF_BASE_TAG)
	docker push $(OVERLEAF_SLIM_TAG)
	docker push $(OVERLEAF_FULL_TAG)
	docker push $(OVERLEAF_LATEST_TAG)

.PHONY: all build-base build-community build-full push
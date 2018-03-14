.PHONY: build

SHELL := /bin/bash
CONTAINERNAME=accli
IMAGENAME=accli

help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

build: ## Build the Docker image
	cp -r requirements.txt ./build
	cp -r config.json ./build
	docker build -t $(IMAGENAME) ./build

up: build ## Bring the Docker container up
	docker run -td -v $(PWD):/opt --name $(CONTAINERNAME) $(IMAGENAME) || echo 'Already up!'

down: ## Stop the Docker container
	docker stop $(CONTAINERNAME)

enter: ## Enter the running Docker container
	docker exec -it $(CONTAINERNAME) /bin/bash

clean: down ## Stop and remove Docker container
	docker rm $(CONTAINERNAME)

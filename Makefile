IMAGE_NAME := sift-dev

.PHONY: dev-image dev dev-ui

dev-image:
	podman build -t $(IMAGE_NAME) .

dev: dev-image
	podman run -it --rm \
		--userns=keep-id \
		-v $(PWD):/workspace \
		-v $(HOME)/.claude:/home/vscode/.claude \
		$(IMAGE_NAME) bash

dev-ui: dev-image
	podman run -it --rm \
		--userns=keep-id \
		-v $(PWD):/workspace \
		-v $(HOME)/.gitconfig:/home/vscode/.gitconfig \
		-v $(HOME)/.claude:/home/vscode/.claude \
		$(IMAGE_NAME) zellij --layout .zellij/dev.kdl

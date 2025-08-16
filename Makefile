# Makefile für MC-Test App (lokaler Scope)

.PHONY: deploy deploy-remote

REMOTE ?= github

deploy:
	./mc_test_app/deploy.sh $(REMOTE)

deploy-remote: deploy

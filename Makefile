# Makefile für MC-Test App

.PHONY: deploy clean

# Standard-Deploy (nutzt deploy.sh und Remote 'github')
deploy:
	./deploy.sh github

# Alternative: anderes Remote
# make deploy REMOTE=origin

REMOTE ?= github

deploy-remote:
	./deploy.sh $(REMOTE)

# Aufräumen temporärer Artefakte (falls später ergänzt)
clean:
	@echo "Nichts zu reinigen"

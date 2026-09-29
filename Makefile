.DEFAULT_GOAL := help
MAKEFLAGS += --no-print-directory
.PHONY: check ci clean help init release sync sync-readme

UV ?= uv
VENV_DIR := .venv

## Show available commands.
help:
	@echo ""
	@echo "Pre Commit Hooks"
	@echo ""
	@echo "Usage:"
	@echo "  make <target>"
	@echo ""
	@echo "Typical workflow:"
	@echo "  make init                     Set up the project and development environment"
	@echo "  make check                    Format and run quality checks"
	@echo "  make ci                       Run the checks and the test suite"
	@echo "  make clean                    Remove build artifacts and untracked files"
	@echo ""
	@echo "Release:"
	@echo "  make release                  Bump the version, sync the README, and tag (push manually)"
	@echo ""
	@echo "All targets:"
	@awk '/^## / {desc=$$0; sub(/^## /,"",desc)} /^[a-zA-Z_-]+:/ {target=$$1; sub(/:$$/,"",target); printf "  %-28s %s\n", target, desc; desc=""}' $(MAKEFILE_LIST) | sort
	@echo ""

## Synchronize dependencies and install development tools.
sync: pyproject.toml
	$(UV) sync --group dev --quiet
	$(UV) run --quiet prek install

## Run code quality checks.
check:
	@$(UV) lock --check
	@$(UV) run --quiet python scripts/check.py

# Mark the commands below as running in CI so tools that adapt to it can tell.
# An existing CI value wins, so a provider's own setting is never overwritten.
## Run the checks and the test suite under coverage.
ci: export CI := $(if $(CI),$(CI),true)
ci: check
	@$(UV) run --quiet coverage run -m pytest -q
	@$(UV) run --quiet coverage report

## Remove build artifacts and untracked files (keeps the .venv folder and .env files).
clean:
	@$(UV) run --quiet python scripts/clean.py

## Initialize a Git repository, install dependencies, and create the initial commit.
init:
	@$(UV) run --quiet python scripts/init.py
	@$(UV) run --quiet python scripts/update_github_metadata.py
	@$(UV) run --quiet python scripts/update_vscode_extensions.py

## Sync the README install snippet's rev with the pyproject version.
sync-readme:
	@$(UV) run --quiet python scripts/sync_readme_rev.py

## Bump the version, sync the README, and tag the release.
release:
	$(UV) sync --group dev --quiet
	@if ! git diff --quiet || ! git diff --cached --quiet; then \
		echo "Git tree is not clean. Commit or stash changes first."; \
		exit 1; \
	fi
	@$(MAKE) check
	$(UV) run --quiet cz bump
	@if ! git diff --quiet -- README.md; then \
		TAG=$$(git tag --points-at HEAD --sort=-creatordate | head -n 1); \
		if [ -n "$$TAG" ]; then \
			TYPE=$$(git cat-file -t "$$TAG"); \
			MSG=$$(git tag -l --format='%(contents)' "$$TAG"); \
			git add README.md; \
			git commit --amend --no-edit --no-verify >/dev/null; \
			git tag -d "$$TAG" >/dev/null; \
			if [ "$$TYPE" = "tag" ]; then \
				printf '%s\n' "$$MSG" | git tag -a -F - "$$TAG" >/dev/null; \
			else \
				git tag "$$TAG" >/dev/null; \
			fi; \
			echo "Folded the synced README into the bump commit and retagged $$TAG."; \
		fi; \
	fi
	@echo ""
	@echo "Review the bump, then publish with:"
	@echo "  git push && git push --tags"

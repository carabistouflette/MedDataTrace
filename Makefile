.PHONY: setup test lint format check-templates check spec

setup:
	uv sync --locked

test:
	uv run --locked python -m unittest discover -s research/specs/reference_semantics -v

lint:
	uv run --locked ruff check research/specs/reference_semantics
	uv run --locked ruff format --check research/specs/reference_semantics

format:
	uv run --locked ruff check --fix research/specs/reference_semantics
	uv run --locked ruff format research/specs/reference_semantics

check-templates:
	uv run --locked python -m json.tool research/specs/pilot_templates/effort_record.template.json >/dev/null
	uv run --locked python -m json.tool research/specs/pilot_templates/operational_record.json >/dev/null
	uv run --locked python -m json.tool research/specs/pilot_templates/reference_labels.WITHHOLD.template.json >/dev/null
	uv run --locked python -m json.tool research/specs/pilot_templates/study_record.template.json >/dev/null
	uv run --locked python -m json.tool research/specs/pilot_templates/track_r.synthetic.json >/dev/null

check: lint test check-templates

spec:
	@missing=0; \
	for tool in latexmk biber; do \
		if ! command -v "$$tool" >/dev/null 2>&1; then \
			echo "Missing required TeX prerequisite: $$tool" >&2; \
			missing=1; \
		fi; \
	done; \
	if [ "$$missing" -ne 0 ]; then \
		echo "Install both latexmk and biber, then rerun make spec." >&2; \
		echo "Without local TeX packages, use the GitHub Actions Specification job to build the PDF." >&2; \
		exit 1; \
	fi
	cd research/specs && latexmk -pdf -interaction=nonstopmode -halt-on-error meddatatrace_specification.tex

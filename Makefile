# Regenerate the profile images. Needs Python 3.11+ with scripts/requirements.txt (fonttools, brotli).
#   make assets              everything that only depends on files in this repo (what the assets workflow runs)
#   make homelab activity    the two data-driven cards (homelab needs data/live.json, activity needs a GitHub token)
PYTHON ?= python3
S = scripts

.PHONY: assets hero canfd iso trace sections homelab activity readme

assets: hero canfd iso trace sections readme

hero:
	cd $(S) && $(PYTHON) hero3d.py
canfd:
	cd $(S) && $(PYTHON) canfd.py
iso:
	cd $(S) && $(PYTHON) iso.py
trace:
	cd $(S) && $(PYTHON) trace.py
sections:
	cd $(S) && $(PYTHON) sections.py
homelab:
	cd $(S) && $(PYTHON) homelab.py
activity:
	cd $(S) && $(PYTHON) activity.py
readme:
	cd $(S) && $(PYTHON) readme.py

get-hacking:
	# needed for broken lib deps on fedora 34
	PIP_INSTALL_OPTION="-- --no-jack" pipenv install --dev --skip-lock python-rtmidi
	pipenv install --dev

flatpak-build:
	flatpak-builder ./build  com.verynoisy.najork.yml --force-clean

flatpak-debug: flatpak-build
	flatpak-builder --verbose --run ./build com.verynoisy.najork.yml /app/bin/najork

debug:
	PYTHONPATH=.:${PYTHONPATH} python bin/najork-debug

test:
	PYTHONPATH=.:${PYTHONPATH} python -m pytest tests/ --cov=najork

trace:
	PYTHONPATH=.:${PYTHONPATH} python -m pytest tests/ --cov=najork --trace

pdb:
	PYTHONPATH=.:${PYTHONPATH} python -m pytest tests/ --cov=najork --pdb

.PHONY: flatpak-build flatpak-debug debug test

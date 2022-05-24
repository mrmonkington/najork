get-hacking: poetry.lock
	# needed for broken lib deps on fedora 34
	#PIP_INSTALL_OPTION="-- --no-jack" pipenv install --dev --skip-lock python-rtmidi
	#pipenv install --dev
	poetry install

flatpak-build:
	flatpak-builder ./build  com.verynoisy.najork.yml --force-clean

flatpak-debug: flatpak-build
	flatpak-builder --verbose --run ./build com.verynoisy.najork.yml /app/bin/najork

debug: get-hacking
	PYTHONPATH=.:${PYTHONPATH} python bin/najork-debug

test: get-hacking
	PYTHONPATH=.:${PYTHONPATH} python -m pytest tests/ --cov=najork

trace: get-hacking
	PYTHONPATH=.:${PYTHONPATH} python -m pytest tests/ --cov=najork --trace

pdb: get-hacking
	PYTHONPATH=.:${PYTHONPATH} python -m pytest tests/ --cov=najork --pdb

.PHONY: flatpak-build get-hacking flatpak-debug debug test trace pdb

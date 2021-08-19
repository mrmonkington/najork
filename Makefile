
flatpak-build:
	flatpak-builder ./build  com.verynoisy.najork.yml --force-clean

flatpak-debug: flatpak-build
	flatpak-builder --verbose --run ./build com.verynoisy.najork.yml /app/bin/najork

debug:
	PYTHONPATH=.:${PYTHONPATH} python bin/najork-debug

test:
	PYTHONPATH=.:${PYTHONPATH} python -m pytest tests/ --cov=najork

.PHONY: flatpak-build flatpak-debug debug test

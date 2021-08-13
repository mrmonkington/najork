build:
	flatpak-builder ./build  com.verynoisy.najork.yml --force-clean

run: build
	flatpak-builder --verbose --run ./build com.verynoisy.najork.yml /app/bin/najork

debug:
	python bin/najork-debug

test:
	python -m pytest tests/ --cov=najork

.PHONY: build run test

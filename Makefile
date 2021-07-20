build:
	flatpak-builder ./build  com.verynoisy.najork.yml --force-clean

run: build
	flatpak-builder --verbose --run ./build com.verynoisy.najork.yml /app/bin/najork

.PHONY: build run

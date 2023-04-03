.default: build
.PHONY: build
build:
	cd frontend && npx vite build --outDir ../backend/src/playbacker/dist --emptyOutDir
	cd backend && poetry build

.PHONY: clean
clean:
	rm -rf backend/dist backend/src/playbacker/dist

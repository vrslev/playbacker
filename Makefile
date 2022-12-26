.default: build
build:
	cd frontend && npx vite build --outDir ../backend/src/playbacker/dist --emptyOutDir
	cd backend && poetry build

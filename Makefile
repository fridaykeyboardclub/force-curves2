
all: curve-data site

curve-data:
	$(MAKE) -C data-processor csv
	mkdir -p force-curves-site/public/data/
	cp -r data-processor/csv_output force-curves-site/public/data/
	cp data-processor/switchmeta.csv force-curves-site/public/data/

site: clean-docs
	mkdir -p docs/
	cd force-curves-site; npm install; npm run build
	cp -r force-curves-site/dist/* docs/

clean:
	$(MAKE) -C data-processor clean
	rm -rf force-curves-site/dist/
	rm -rf force-curves-site/public/data/

clean-deps: clean
	rm -rf data-processor/venv/
	rm -rf force-curves-site/node_modules/

clean-docs:
	rm -rf docs

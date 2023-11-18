
csv:
	env VIRTUAL_ENV=./venv venv/bin/python3 generate.py

images:
	env VIRTUAL_ENV=./venv venv/bin/python3 generate.py --generate-images
	pandoc image_output/000_curves.md -f gfm -t html -s -o image_output/index.html --metadata title="Force Curves"

clean:
	rm -rf image_output csv_output


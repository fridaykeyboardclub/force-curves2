
csv:
	./generate.py

images:
	./generate.py --generate-images
	pandoc image_output/000_curves.md -f gfm -t html -s -o image_output/index.html --metadata title="Force Curves"

clean:
	rm -rf image_output csv_output


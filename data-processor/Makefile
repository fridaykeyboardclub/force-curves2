
all:
	./generate.py
	pandoc image_output/000_curves.md -f gfm -t html -s -o image_output/000_curves.html --metadata title="Force Curves"

clean:
	rm -rf image_output csv_output


# Force Curves Comparison

A little site that allows for comparison of force curves for mechanical keyboard switches, using data from
[ThereminGoat](https://github.com/ThereminGoat/force-curves).

## About

#### data-processor

This directory contains a python script for processing the force curve data from ThereminGoat's repository. It also
can optionally generate static images and a markdown file using the option `--generate-images` on the command line.

#### force-curves-site

This is the code for the site, written with Vue and displaying graphs using Chart.js.

## Building

### Setup

1. Initialise the submodule: `git submodule init && git submodule update`
2. In data-processor/, install the venv with `python -m venv venv`, activate it, and install the dependencies in requirements.txt

### Build

```
make
```
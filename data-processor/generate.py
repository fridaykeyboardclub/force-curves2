#! /usr/bin/env python3

import urllib
import os
from dataclasses import dataclass
from os.path import dirname, join
import csv
from matplotlib import pyplot as plot

@dataclass
class CsvData:
    data_x: list[float]
    data_y: list[float]

@dataclass
class SwitchData:
    name: str

    # Estimated peak 0.2mm before bottom out
    peak_weight_estimate: float

    max_displacement: float

    downstroke: CsvData
    upstroke: CsvData

@dataclass
class SwitchMeta:
    name: str
    type: str # Either "linear", "tactile" or "clicky"

def do_directory_walk():
    print(__file__)
    this_dir = dirname(__file__.replace("/./", "/"))
    print(this_dir)
    rootdir = dirname(this_dir)
    print(rootdir)
    theremingoat_dir = join(rootdir, "force-curves")
    print(theremingoat_dir)

    savedir = join(this_dir, "image_output")
    savedir_csv = join(this_dir, "csv_output")

    if not os.path.exists(savedir):
        os.mkdir(join(this_dir, "image_output"))
        print("Created image output directory")
    if not os.path.exists(savedir_csv):
        os.mkdir(join(this_dir, "csv_output"))
        print("Created CSV output directory")

    markdown_file = open(join(savedir, "000_curves.md"), "w")
    markdown_file.write("From [ThereminGoat](https://github.com/ThereminGoat/force-curves)\n\n")

    all_switches = []

    for switch_dir_name in sorted(os.listdir(theremingoat_dir)):
        switch_dir_path = join(theremingoat_dir, switch_dir_name)
        if switch_dir_name.startswith("."):
            continue
        if not os.path.isdir(switch_dir_path):
            continue

        files_in_dir = os.listdir(switch_dir_path)
        csv_files = [x for x in files_in_dir
                     if x.endswith(".csv")
                        and not x.endswith("HighResolutionRaw.csv")
                        and not x.endswith("HighResoultionRaw.csv")
                        and not x.endswith("HighResolution.csv")
                    ]
        try:
            csv_file = csv_files[0] # Only use the first csv found
        except IndexError:
            continue

        print(csv_file)
        csv_path = join(switch_dir_path, csv_file)
        switch_data = read_csv_data(csv_path, switch_dir_name)

        all_switches.append(switch_dir_name)

        create_image(savedir, switch_dir_name, switch_data)
        create_csv_files(savedir_csv, switch_dir_name, switch_data)

        escaped_filename = urllib.parse.quote(switch_dir_name)
        markdown_file.write("### %s\n\n![%s](%s.png)\n\n" % (switch_dir_name, switch_dir_name, escaped_filename))

    markdown_file.close()

    switch_metadatas = []
    with open(join(this_dir, "switchmeta.csv"), "r") as switch_meta_file:
        metareader = csv.reader(switch_meta_file)
        switch_metadatas = [SwitchMeta(x[0], x[1] or None) for x in metareader]

    new_switch_metadatas = []
    for switch_name in all_switches:
        switch_meta = None
        try:
            switch_meta = next(x for x in switch_metadatas if x.name == switch_name)
        except StopIteration:
            switch_meta = SwitchMeta(switch_name, "")
        new_switch_metadatas.append(switch_meta)
        if switch_meta.type == "":
            print("Switch type missing for switch %s" % (switch_name,))

    with open(join(this_dir, "switchmeta.csv"), "w") as switch_meta_file:
        metawriter = csv.writer(switch_meta_file)
        for switch_meta in new_switch_metadatas:
            metawriter.writerow([switch_meta.name, switch_meta.type])

def read_csv_data(file: str, name: str) -> SwitchData:
    with open(file) as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        data_downstroke_x = []
        data_downstroke_y = []
        data_upstroke_x = []
        data_upstroke_y = []
        max_x = 0.0
        data_reversed = False
        correction = None
        data_points_read = 0

        for row in reader:
            # The first few rows aren't readable data, the data lines start with ints
            try:
                index = int(row[0])
            except ValueError:
                continue

            data_points_read += 1

            if row[5] == "OK": # indicates good data
                displacement = float(row[3])
                weight = float(row[1])

                if not data_reversed:
                    # Identify a correction if necessary, assume zero is the point where the force goes over 2g
                    if correction is None:
                        if weight > 2.0:
                            correction = displacement
                        else:
                            continue

                    corrected_displacement = displacement - correction
                    data_downstroke_x.append(corrected_displacement)
                    data_downstroke_y.append(weight)

                    if corrected_displacement >= max_x:
                        max_x = corrected_displacement
                    else:
                        # The data has started going back down again
                        data_reversed = True

                if data_reversed:
                    corrected_displacement = displacement - correction
                    if corrected_displacement >= 0:
                        data_upstroke_x.append(corrected_displacement)
                        data_upstroke_y.append(weight)


        downstroke_csv = CsvData(data_downstroke_x, data_downstroke_y)
        peak_before_bottom_out_estimate = peak_estimate(downstroke_csv)
        max_displacement = data_downstroke_x[-1]

        print("%s data points read, %s ignored" % (
            data_points_read,
            data_points_read - len(data_downstroke_x) - len(data_upstroke_x),
        ))
        print("correction from zero: %s" % (correction,))
        print("estimated peak %s" % (peak_before_bottom_out_estimate,))

        return SwitchData(
            name = name,
            peak_weight_estimate= peak_before_bottom_out_estimate,
            max_displacement = max_displacement,
            downstroke = downstroke_csv,
            upstroke = CsvData(list(reversed(data_upstroke_x)), list(reversed(data_upstroke_y))),
        )

def peak_estimate(downstroke: CsvData) -> float:
    # Scan the list backwards to get a point 0.2mm before the data reversed
    i = 0
    last_x = downstroke.data_x[-1]
    for x_value in reversed(downstroke.data_x):
        i -= 1
        if x_value < last_x - 0.2:
            break
    # Find the max value up to that point
    return max(downstroke.data_y[0:i])

def create_image(savedir: str, name: str, data: SwitchData):
    upstroke_line = plot.plot(data.upstroke.data_x, data.upstroke.data_y)
    downstroke_line = plot.plot(data.downstroke.data_x, data.downstroke.data_y)

    plot.setp(upstroke_line, color="lightblue")
    plot.setp(downstroke_line, color="tab:blue")

    plot.title(name)
    x_axis_max = 100
    if data.peak_weight_estimate > 170:
        x_axis_max = 240
    elif data.peak_weight_estimate > 125:
        x_axis_max = 200
    elif data.peak_weight_estimate > 90:
        x_axis_max = 140
    y_axis_max = 4.5 if data.max_displacement < 4.4 else 5.5
    plot.axis([0.0, y_axis_max, 0.0, x_axis_max])
    plot.grid(visible=True)
    savename = name + ".png"
    plot.savefig(join(savedir, savename))
    plot.clf()

def create_csv_files(savedir: str, name: str, data: SwitchData):
    def write_csv_data_file(filename: str, csv_data: CsvData):
        with open(filename, "w") as datafile:
            csvwriter = csv.writer(datafile)
            for index in range(0, len(csv_data.data_x)):
                csvwriter.writerow([
                    "%.4f" % (csv_data.data_x[index],),
                    "%.4f" % (csv_data.data_y[index],)
                ])

    downstroke_file = join(savedir, name + ".downstroke.csv")
    upstroke_file = join(savedir, name + ".upstroke.csv")
    write_csv_data_file(downstroke_file, data.downstroke)
    write_csv_data_file(upstroke_file, data.upstroke)

if __name__ == "__main__":
    do_directory_walk()


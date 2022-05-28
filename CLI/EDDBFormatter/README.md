# HalpyBOT EDDB Station Formatter

# Description
This program formats EDDB populated system and station dumps into a record of all stations in the 
galaxy that have repair functionality, and meet the other requirements to qualify as a diversion 
station for Code Black rescues. The output file will contain the station name, system the station 
is in, coordinates of the system, and the distance from the main star of the station.

# Installation

## Requirements
- Python 3.8+
- Populated Systems EDDB data dump found [On Their Website](https://eddb.io/archive/v6/systems_populated.json)
- Station Listing EDDB data dump found [On Their Website](https://eddb.io/archive/v6/stations.json)

## Usage
- Download the required files.
- [Optional] it is strongly encouraged to run the files through a processing program such as [jq](https://stedolan.github.io/jq/).
  - Ex, `jq . systems_populated.json > formatted_systems_populated.json`
- Rename the files, if required.
- From the CLI directory, run the program with `python .\EDDBFormatter\`.
- The program will automatically filter out planetary outposts, fleet carriers, non-large landing pads, stations too far from the main star, and other factors.
- The output files will be located in the `files\output` subdirectory.

# Authors and Acknowledgements
- Written by [David Sangrey](https://gitlab.com/rixxan)

# License
This project is governed under the GNU General Public License v3.0 license.

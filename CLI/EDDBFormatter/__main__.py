"""
HalpyBOT CLI

EDDB File Formatter

Copyright (c) 2022 The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md
"""
import os.path
import json
import sys
from tqdm import tqdm


def run():
    """Run the EDDB Formatter"""
    print(
        "=" * 20
        + "\nCopyright (c) 2022 The Hull Seals\nEDDB File Formatter for HalpyBOT\n"
        + "=" * 20
        + "\n"
    )
    print(
        "WARNING: This operation will remove the existing generated files, and relies on filtered data dumps from "
        "EDDB to proceed. \n "
    )
    cont = input(
        "Please make a backup of the previously generated files first. Do you wish to proceed? (Y/n) "
    )
    if cont.upper() != "Y":
        print("Roger, aborting...")
        sys.exit()

    # Remove Old Files
    if os.path.exists("EDDBFormatter/files/filtered_stations.json"):
        os.remove("EDDBFormatter/files/filtered_stations.json")

    if os.path.exists("EDDBFormatter/files/filtered_systems_populated.json"):
        os.remove("EDDBFormatter/files/filtered_systems_populated.json")

    with open("EDDBFormatter/files/formatted_systems_populated.json", "r") as systemfile:
        system_data = json.load(systemfile)
        third_dict = {}
        counter = 1
        for key_2 in tqdm(system_data):
            temp_dict_2 = {
                "id": key_2["id"],
                "system_name": key_2["name"],
                "x_coord": key_2["x"],
                "y_coord": key_2["y"],
                "z_coord": key_2["z"],
                "needs_permit": key_2["needs_permit"],
            }
            if temp_dict_2["needs_permit"] is not True:
                third_dict[counter] = temp_dict_2
                counter += 1

        with open("EDDBFormatter/files/filtered_systems_populated.json", "w") as system_file:
            json.dump(third_dict, system_file, indent=2)

    with open("EDDBFormatter/files/formatted_stations.json", "r") as jsonfile:
        data = json.load(jsonfile)
        second_dict = {}
        counter = 1
        for key in tqdm(data):
            temp_dict = {
                "id": key["id"],
                "name": key["name"],
                "system_id": key["system_id"],
                "max_landing": key["max_landing_pad_size"],
                "dist_star": key["distance_to_star"],
                "has_repair": key["has_repair"],
                "is_planet": key["is_planetary"],
                "station_type": key["type"],
            }
            # for system in temp_dict_2:
            #     if system['id'] == temp_dict['system_id']:
            #         temp_dict.update(system)
            if (
                temp_dict["max_landing"] == "L"
                and temp_dict["has_repair"] is True
                and temp_dict["is_planet"] is False
                and temp_dict["station_type"] != "Fleet Carrier"
            ):
                second_dict[counter] = temp_dict
                counter += 1

        print("Read complete. Processing now...")
        with open("EDDBFormatter/files/filtered_stations.json", "w") as json_file:
            json.dump(second_dict, json_file, indent=2)


if __name__ == "__main__":
    # Tool may not be run from any other folder than CLI/ see CLI/BackupFactUpdater/__main__.py
    if not os.getcwd().endswith("CLI"):
        print("Please run this tool from the /CLI folder, with `python3 EDDBFormatter`")
        sys.exit()
    try:
        run()
    except KeyboardInterrupt:
        sys.exit()

"""
HalpyBOT CLI

EDDB File Formatter

Copyright (c) The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md
"""
import os.path
import json
import sys
import pathlib
from tqdm import tqdm


def run():
    """Run the EDDB Formatter"""
    rootpath = pathlib.PurePath(__file__).parent
    rootpath = str(rootpath).replace("\\", "/")
    print(
        f"{'='*20}\n"
        f"Copyright (c) 2022 The Hull Seals\n"
        f"EDDB File Formatter for HalpyBOT\n"
        f"{'='*20}\n"
        f"WARNING: This operation will remove the existing generated files, "
        f"and relies on filtered data dumps from EDDB to proceed.\n "
    )
    cont = input(
        "Please make a backup of the previously generated files first. "
        "Do you wish to proceed? (Y/n) "
    )
    if cont.upper() != "Y":
        print("Roger, aborting...")
        sys.exit()

    # Remove Old Files
    if os.path.exists(f"{rootpath}/files/output/filtered_stations.json"):
        os.remove(f"{rootpath}/files/output/filtered_stations.json")

    if os.path.exists(f"{rootpath}/files/output/filtered_systems_populated.json"):
        os.remove(f"{rootpath}/files/output/filtered_systems_populated.json")

    if os.path.exists(
        f"{rootpath}/files/output/filtered_combined_stations_with_systems.json"
    ):
        os.remove(
            f"{rootpath}/files/output/filtered_combined_stations_with_systems.json"
        )

    # Open the jq-formatted (or renamed) json system json file. (Original Size: 57 MB)
    with open(
        f"{rootpath}/files/input/formatted_systems_populated.json",
        "r",
        encoding="UTF-8",
    ) as systemfile:
        system_data = json.load(systemfile)
    system_dict = {}
    for system in tqdm(system_data, desc="Filtering System Data: "):
        # Filter down to just key system keys
        temp_system_dict = {
            "id": system["id"],
            "system_name": system["name"],
            "x_coord": system["x"],
            "y_coord": system["y"],
            "z_coord": system["z"],
            "needs_permit": system["needs_permit"],  # Included for filtering only.
        }
        if not temp_system_dict["needs_permit"]:
            system_dict[system["id"]] = temp_system_dict

    # Create output filtered system file, in case we want to review it later.
    with open(
        f"{rootpath}/files/output/filtered_systems_populated.json",
        "w",
        encoding="UTF-8",
    ) as system_file:
        json.dump(system_dict, system_file, indent=2)

    # Open jq-formatted or renamed station file. (Original Size: 420 MB)
    with open(
        f"{rootpath}/files/input/formatted_stations.json", "r", encoding="UTF-8"
    ) as jsonfile:
        data = json.load(jsonfile)
    station_dict = {}
    counter = 1
    for key in tqdm(data, desc="Filtering Station Data: "):
        temp_station_dict = {
            "id": key["id"],
            "name": key["name"],
            "system_id": key["system_id"],
            "max_landing": key["max_landing_pad_size"],
            "dist_star": key["distance_to_star"],
            "has_repair": key["has_repair"],
            "is_planet": key["is_planetary"],
            "station_type": key["type"],
        }
        # To be used as a diversion station, must have L pad, Repair function,
        # not on a planet, not a mobile platform, and no more than 800 LS from the main star.
        if (
            temp_station_dict["max_landing"] == "L"
            and temp_station_dict["has_repair"]
            and not temp_station_dict["is_planet"]
            and temp_station_dict["station_type"] != "Fleet Carrier"
            and temp_station_dict["dist_star"] <= 800
        ):
            station_dict[counter] = temp_station_dict
            counter += 1
    # Create output filtered station file, in case we want to review it later.
    with open(
        f"{rootpath}/files/output/filtered_stations.json", "w", encoding="UTF-8"
    ) as json_file:
        json.dump(station_dict, json_file, indent=2)

    # Now we need to combine the two dicts to a formatted list file.
    write_list = []
    # LIST not a DICT. Otherwise, it won't work well with the dataclass
    # we're actually using in the bot. (Found that out the hard way...)
    for counter, key in enumerate(
        tqdm(station_dict, desc="Combining System Files: "), start=1
    ):
        working_dict_1 = station_dict[counter]
        try:
            wd_2 = system_dict[station_dict[counter]["system_id"]]
        except KeyError:  # If a system has no valid stations in it, pass and move on.
            continue
            # Drop what we don't want.
        final_dict = {
            "name": working_dict_1["name"],
            "dist_star": working_dict_1["dist_star"],
            "system_name": wd_2["system_name"],
            "x_coord": wd_2["x_coord"],
            "y_coord": wd_2["y_coord"],
            "z_coord": wd_2["z_coord"],
        }
        write_list.append(final_dict)  # Append as List, not write as full Dict
    # Write it out before we forget what we're doing.
    with open(
        f"{rootpath}/files/output/filtered_combined_stations_with_systems.json",
        "w",
        encoding="UTF-8",
    ) as json_file:
        json.dump(write_list, json_file, indent=2)

    print(
        "Operation Complete! Please validate the file manually before deploying to production."
    )


if __name__ == "__main__":
    try:
        run()
    except KeyboardInterrupt:
        sys.exit()

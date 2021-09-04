"""
HalpyBOT CLI

carrier.py - DSSA carrier object

Copyright (c) 2021 The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md
"""

from typing import Optional, Dict
import requests

class EDSMLookupError(Exception):
    pass

class DSSACarrier:
    """
    DSSA carrier object, as parsed from an external data source
    """

    def __init__(self, name: str = "Unknown", call: str = "Unknown", status: int = 0, location: str = "Unknown",
                 region: str = "Unknown", owner: str = "Unknown/Independent", decom_date: str = "Unknown"):
        """Initialize new DSSA carrier object

        Args:
            name (str): Carriers name, including prefix
            call (str): FC call sign, formatted XXX-XXX
            status (int): carriers current operational status
                * 0 Unknown
                * 1 Pre-planning
                * 2 Preperation
                * 3 All systems go
                * 4 Carrier operational
                * 5 Other
            location (str):
            region (str):
            owner (str): Owner group, not owning CMDR
            decom_date (str): decommissioning date
        """
        self._marked_manual = False
        self._location = location
        try:
            self._coords, self._has_system = self._get_coords(self._location), True
        except EDSMLookupError:
            raise
        if not self._coords:

            self._marked_manual, self._has_system = True, False
        self._name = name
        self._call = call
        self.status = status
        self.region = region
        self.owner = owner
        self.decom_date = decom_date

    def __eq__(self, other):
        """Compare two carriers by name

        Will always return False if compared with a non-DSSACarrier object

        Args:
            other: Other fleet carrier object

        Returns:
            (bool): True if names are the same, else False

        """
        if not isinstance(other, DSSACarrier):
            return False
        return self.name.lower() == other.name.lower()

    def __repr__(self):
        """Return a string representation of the carrier

        Returns:
            (str): string representation of the carrier

        """
        return f"DSSACarrier({self._name=}, {self._location=}, {self._has_system=}, {self._coords=}," \
               f"{self.status=}, {self.owner=}, {self.region=}, {self.decom_date=})"

    @property
    def coordinates(self) -> Optional[Dict]:
        """System coordinates

        Returns:
            (dict or None): a diction

        """
        return self._coords

    @property
    def name(self) -> str:
        """System name, synced with EDSM

        Returns:
            (str): System name

        """
        return self._name

    @property
    def callsign(self) -> str:
        """Carrier callsign

        Returns:
            (str): FC's call sign, formatted XXX-XXX

        """
        return self._call

    @property
    def has_system(self) -> bool:
        """Checks if a system could be found in EDSM this carrier

        Returns:
            (bool): True if a system could be found, else False

        """
        return self._has_system

    def _get_coords(self, system: str) -> Optional[Dict]:
        """Get coordinates from EDSM

        Args:
            system (str): System name

        Returns:
            (dict or None): Coordinates if system can be found, else `None`

        """
        try:
            response = requests.get("https://www.edsm.net/api-v1/system",
                                    params={"systemName": system,
                                            "showCoordinates": 1,
                                            "showInformation": 1}, timeout=5)
            responses = response.json()

        except requests.exceptions.RequestException:
            raise EDSMLookupError("Unable to verify system, having issues connecting to the EDSM API.")

        # Return None if system doesn't exist
        if len(responses) == 0:
            return None
        else:
            self._name = responses['name']  # Update name for consistency
            return responses['coords']

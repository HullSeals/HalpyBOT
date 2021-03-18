from __future__ import annotations
import requests
import numpy as np
import logging
from dataclasses import dataclass

from typing import Optional
from ..datamodels.edsm_classes import SystemInfo, Coordinates

class EDSMLookupError(Exception):
    """
    Base class for lookup errors
    """

class NoResultsEDSM(EDSMLookupError):
    """
    No results for the given query were found with the EDSM API
    """

class EDSMConnectionError(EDSMLookupError):
    """
    Request failed due to an exception that occurred
    while connecting to the EDSM API
    """

@dataclass(frozen=True)
class GalaxySystem:
    name: str
    coords: Coordinates
    coordsLocked: bool
    information: SystemInfo

    @classmethod
    async def get_info(cls, name) -> Optional[GalaxySystem]:
        try:
            response = requests.get("https://www.edsm.net/api-v1/system",
                                    params={"systemName": name.strip(),
                                            "showCoordinates": 1,
                                            "showInformation": 1})
            responses = response.json()

        except requests.exceptions.RequestException as er:
            logging.error(f"EDSM: Error in `system get_info()` lookup: {er}", exc_info=True)
            raise EDSMConnectionError("Unable to verify system, having issues connecting to the EDSM API.")

        # Return None if system doesn't exist
        if len(responses) == 0:
            return None
        else:
            return cls(**responses)

    @classmethod
    async def exists(cls, name):
        obj = await cls.get_info(name)
        if obj is None:
            return False
        else:
            return True


async def locatecmdr(cmdrname):

    try:
        response = requests.get("https://www.edsm.net/api-logs-v1/get-position",
                                params={"commanderName": cmdrname, "showCoordinates": 1})
        responses = response.json()

        if responses['msgnum'] == 203:
            raise NoResultsEDSM("CMDR not found or not sharing location on EDSM")

        LastSeenSystem = responses['system']
        LastSeenDate = responses['date']

    except requests.exceptions.RequestException as er:
        logging.error(f"EDSM: Error in `system_exists()` lookup: {er}", exc_info=True)
        raise EDSMConnectionError("Error! Unable to verify system.")

    if LastSeenDate is None:
        LastSeenDate = "an unknown date and time."

    return LastSeenSystem, LastSeenDate


# TODO Split this behemoth up into multiple functions and refactor
async def checkdistance(sysa, sysb):
    sysax, sysay, sysaz, sysbx, sysby, sysbz, syserr, sysastat, sysbstat = 0, 0, 0, 0, 0, 0, 0, 0, 0
    # TODO simplify try-except block and handle exceptions the proper way
    try:
        query1 = requests.get("https://www.edsm.net/api-v1/systems",
                              params={"systemName[]": sysa, "showCoordinates": 1})
        res1 = query1.json()
        query2 = requests.get("https://www.edsm.net/api-v1/systems",
                              params={"systemName[]": sysb, "showCoordinates": 1})
        res2 = query2.json()
        try:
            if res1:
                sysax = res1[0]['coords']['x']
                sysay = res1[0]['coords']['y']
                sysaz = res1[0]['coords']['z']
                sysastat = "Valid System"
            else:
                sysastat = "System Not Found in EDSM."
        except KeyError:
            sysastat = "System has no Coordinates."
        try:
            if res2:
                sysbx = res2[0]['coords']['x']
                sysby = res2[0]['coords']['y']
                sysbz = res2[0]['coords']['z']
                sysbstat = "Valid System"
            else:
                sysbstat = "System Not Found in EDSM."
        except KeyError:
            sysbstat = "System has no Coordinates."
    except requests.exceptions.Timeout:
        syserr = "EDSM Timed Out. Unable to verify System."
    except requests.exceptions.TooManyRedirects:
        syserr = "EDSM Didn't Respond. Unable to verify System."
    except ValueError:
        syserr = "Unable to verify System. JSON Decoding Failure."
    except requests.exceptions.RequestException:
        syserr = "Unable to verify system."
    if sysastat != "Valid System":
        try:
            parameters = {"commanderName": sysa, 'showCoordinates': 1}
            query3 = requests.get("https://www.edsm.net/api-logs-v1/get-position", params=parameters)
            res3 = query3.json()
            if res3:
                sysax = res3['coordinates']['x']
                sysay = res3['coordinates']['y']
                sysaz = res3['coordinates']['z']
                sysastat = "Valid System"
            else:
                sysastat = "CMDR or System Not Found in EDSM."
        except KeyError:
            sysastat = "CMDR or System Not Found in EDSM."
        except requests.exceptions.Timeout:
            syserr = "EDSM Timed Out. Unable to verify System."
        except requests.exceptions.TooManyRedirects:
            syserr = "EDSM Didn't Respond. Unable to verify System."
        except ValueError:
            syserr = "Unable to verify System. JSON Decoding Failure."
        except requests.exceptions.RequestException:
            syserr = "Unable to verify system."
    if sysbstat != "Valid System":
        try:
            parameters = {"commanderName": sysb, 'showCoordinates': 1}
            query4 = requests.get("https://www.edsm.net/api-logs-v1/get-position", params=parameters)
            res4 = query4.json()
            if res4:
                sysbx = res4['coordinates']['x']
                sysby = res4['coordinates']['y']
                sysbz = res4['coordinates']['z']
                sysbstat = "Valid System"
            else:
                sysbstat = "CMDR or System Not Found in EDSM."
        except KeyError:
            sysbstat = "CMDR or System Not Found in EDSM."
        except requests.exceptions.Timeout:
            syserr = "EDSM Timed Out. Unable to verify System."
        except requests.exceptions.TooManyRedirects:
            syserr = "EDSM Didn't Respond. Unable to verify System."
        except ValueError:
            syserr = "Unable to verify System. JSON Decoding Failure."
        except requests.exceptions.RequestException:
            syserr = "Unable to verify system."
    if sysastat == "Valid System" and sysbstat == "Valid System":
        distancecheck = await calc_distance(sysax, sysbx, sysay, sysby, sysaz, sysbz)
        distancecheck = f'{distancecheck:,}'
        distancecheck = "The distance between " + sysa + " and " + sysb + " is " + distancecheck + " LY"
    elif syserr != 0:
        distancecheck = "System Error: " + syserr
    elif sysastat == sysbstat:
        distancecheck = "Error! Both points failed: "+sysastat
    else:
        distancecheck = "ERROR! SysA: " + sysastat + " SysB: " + sysbstat
    return distancecheck

# TODO refactor and split up
async def checklandmarks(sysa):
    para0 = {"systemName[]": sysa, "showCoordinates": 1}
    sysax, sysay, sysaz, syserr, sysastat = 0, 0, 0, 0, 0
    try:
        query1 = requests.get("https://www.edsm.net/api-v1/systems", params=para0)
        res1 = query1.json()
        if res1:
            sysax = res1[0]['coords']['x']
            sysay = res1[0]['coords']['y']
            sysaz = res1[0]['coords']['z']
            sysastat = "Valid System"
        else:
            sysastat = "System Not Found in EDSM."
    except KeyError:
        sysastat = "System has no Coordinates."
    except requests.exceptions.Timeout:
        syserr = "EDSM Timed Out. Unable to verify System."
    except requests.exceptions.TooManyRedirects:
        syserr = "EDSM Didn't Respond. Unable to verify System."
    except ValueError:
        syserr = "Unable to verify System. JSON Decoding Failure."
    except requests.exceptions.RequestException:
        syserr = "Unable to verify system."
    if sysastat != "Valid System":
        try:
            parameters = {"commanderName": sysa, 'showCoordinates': 1}
            query3 = requests.get("https://www.edsm.net/api-logs-v1/get-position", params=parameters)
            res3 = query3.json()
            if res3:
                sysax = res3['coordinates']['x']
                sysay = res3['coordinates']['y']
                sysaz = res3['coordinates']['z']
                sysastat = "Valid System"
            else:
                sysastat = "CMDR or System Not Found in EDSM."
        except KeyError:
            sysastat = "CMDR or System Not Found in EDSM."
        except requests.exceptions.Timeout:
            syserr = "EDSM Timed Out. Unable to verify System."
        except requests.exceptions.TooManyRedirects:
            syserr = "EDSM Didn't Respond. Unable to verify System."
        except ValueError:
            syserr = "Unable to verify System. JSON Decoding Failure."
        except requests.exceptions.RequestException:
            syserr = "Unable to verify system."
    if sysastat == "Valid System":
        currclosest = "none"
        maxdist = 10000
        iteration = [0, 1, 2, 3, 4, 5]
        landmarks = ["Sol", "Beagle Point", "Colonia", "Sag A*", "HSRC Limpet's Call", "Galactic East (Chanoa QK-C d14-0)", "Galactic West (Sphiesi HX-L d7-0)"]
        lxcoords = [0, -1111.5625, -9530.5, 25.21875, -681.09375, 39307.25, -42213.8125]
        lycoords = [0, -134.21875, -910.28125, -20.90625, -950.5625, -92.4375, -19.21875]
        lzcoords = [0, 65269.75, 19808.125, 25899.96875, 34219.34375,19338.375, 35418.71875]
        for i in iteration:
            currlandmark = landmarks[i]
            lmx = lxcoords[i]
            lmy = lycoords[i]
            lmz = lzcoords[i]
            distancecheck = await calc_distance(sysax, lmx, sysay, lmy, sysaz, lmz)
            if distancecheck < maxdist:
                currclosest = currlandmark
                maxdist = distancecheck
        if currclosest != "none":
            finaldistance = f'{maxdist:,}'
            return "The closest landmark system is " + currclosest + " at " + finaldistance + " ly."
        else:
            return "No major landmark systems within 10,000 ly."
    elif syserr != 0:
        distancecheck = "System Error: " + syserr
    else:
        distancecheck = "ERROR! " + sysastat
    return distancecheck


async def calc_distance(x1, x2, y1, y2, z1, z2):
    p1 = np.array([x1, y1, z1])
    p2 = np.array([x2, y2, z2])
    squared_dist = np.sum((p1 - p2) ** 2, axis=0)
    dist = np.sqrt(squared_dist)
    dist = np.around(dist, decimals=2, out=None)
    return dist

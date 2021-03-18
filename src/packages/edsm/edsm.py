import requests
import numpy as np


async def checksystem(systemlookup):
    systemlookup = systemlookup.strip()
    parameters = {"systemName": systemlookup}
    try:
        response = requests.get("https://www.edsm.net/api-v1/systems", params=parameters)
        responses = response.json()
        confsys = responses[0]['name']
        if confsys.lower() == systemlookup.lower():
            systemcheck = "System "+systemlookup + " exists in EDSM."
        elif systemlookup.lower() == "mary":
            systemcheck = "Stop it. Get some Help."
        else:
            systemcheck = "System "+systemlookup + " Not Found in EDSM."
    except IndexError:
        systemcheck = "System "+systemlookup + " Not Found in EDSM."
    except requests.exceptions.Timeout:
        systemcheck = "EDSM Timed Out. Unable to verify System."
    except requests.exceptions.TooManyRedirects:
        systemcheck = "EDSM Did Not Respond. Unable to verify System."
    except ValueError:
        systemcheck = "Unable to verify System. JSON Decoding Failure. Maybe the API is down?"
    except requests.exceptions.RequestException:
        systemcheck = "Error! Unable to verify system."
    return systemcheck


async def locatecmdr(cmdrname):
    parameters = {"commanderName": cmdrname, "showCoordinates": 1}
    try:
        response = requests.get("https://www.edsm.net/api-logs-v1/get-position", params=parameters)
        responses = response.json()
        cmdrs = responses['system']
        cmdrd = responses['date']
        try:
            cmdrloc = "CMDR " + cmdrname + " was last seen in " + cmdrs + " on " + cmdrd + " UTC"
        except TypeError:
            cmdrloc = "CMDR Not Found or Not Sharing Location on EDSM"
    except KeyError:
        cmdrloc = "CMDR Not Found or Not Sharing Location on EDSM"
    except requests.exceptions.Timeout:
        cmdrloc = "EDSM Timed Out. Unable to verify System."
    except requests.exceptions.TooManyRedirects:
        cmdrloc = "EDSM Did Not Respond. Unable to verify System."
    except ValueError:
        cmdrloc = "Unable to verify System. JSON Decoding Failure. Maybe the API is down?"
    except requests.exceptions.RequestException:
        cmdrloc = "Error! Unable to verify system."
    return cmdrloc


async def checkdistance(sysa, sysb):
    para0 = {"systemName[]": sysa, "showCoordinates": 1}
    para1 = {"systemName[]": sysb, "showCoordinates": 1}
    sysax, sysay, sysaz, sysbx, sysby, sysbz, syserr, sysastat, sysbstat = 0, 0, 0, 0, 0, 0, 0, 0, 0
    try:
        query1 = requests.get("https://www.edsm.net/api-v1/systems", params=para0)
        res1 = query1.json()
        query2 = requests.get("https://www.edsm.net/api-v1/systems", params=para1)
        res2 = query2.json()
        if res1:
            sysax = res1[0]['coords']['x']
            sysay = res1[0]['coords']['y']
            sysaz = res1[0]['coords']['z']
            sysastat = "Valid System"
        else:
            sysastat = "System Not Found in EDSM."
        if res2:
            sysbx = res2[0]['coords']['x']
            sysby = res2[0]['coords']['y']
            sysbz = res2[0]['coords']['z']
            sysbstat = "Valid System"
        else:
            sysbstat = "System Not Found in EDSM."
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
                sysby = res4['coordinates']['x']
                sysbz = res4['coordinates']['x']
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
        distancecheck = await distancemath(sysax, sysbx, sysay, sysby, sysaz, sysbz)
        distancecheck = "The distance between " + sysa + " and " + sysb + " is " + distancecheck + " LY"
    elif syserr != 0:
        distancecheck = "System Error: " + syserr
    elif sysastat == sysbstat:
        distancecheck = "Error! Both points failed: "+sysastat
    else:
        distancecheck = "ERROR! SysA: " + sysastat + " SysB: " + sysbstat
    return distancecheck


async def distancemath(x1, x2, y1, y2, z1, z2):
    p1 = np.array([x1, y1, z1])
    p2 = np.array([x2, y2, z2])
    squared_dist = np.sum((p1 - p2) ** 2, axis=0)
    dist = np.sqrt(squared_dist)
    dist = np.around(dist, decimals=2, out=None)
    dist = f'{dist:,}'
    return dist

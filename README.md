# HalpyBOT 1.5.2
This is the repository for HalpyBOT, the Hull Seals IRC Chatbot Assistant.

# Description
This repository houses all the files required to build and host your own version of the Hull Seals IRC Chat Assistant, known to us as HalpyBOT. The system is how we manage cases, recite prepared instructions for Clients and Seals, and monitor our IRC network - all in one convenient bot.

This bot is in ACTIVE DEVELOPMENT.

# Installation

## Requirements
* Python 3.8-3.9
* Pydle Python Library
* Asyncio Python Library
* Pure-SASL Python Library
* Setuptools Python Library
* MySQL Python Library
* Numpy Python Library
* Requests Python Library
* Pytest Python Library
* Boto3 Python Library
* Aiohttp Python Library
* Tweepy Python Library

## Usage
To install, download the latest [release](https://gitlab.com/hull-seals-cyberseals/irc/halpybot/-/tags) from our repository. Upload and extract the files to the directory or subdirectory you wish to install from, and create your own config.ini to fit your server, following the example config file provided.

## Troubleshooting
- Upon installation, be sure to replace the information in config.ini to match your own details.
- Additionally, be sure to create a user account and SASL credentials for your IRC user.
- One of the most common sources of issues is your TLS settings in the bot - check these!
- If you are having issues, look through the closed bug reports.
- If no issue is similar, open a new bug report. Be sure to be detailed.
- The notification module will not load if no Amazon Web Services config data is provided.
The bot will run just fine without these, but staff notification functions will not be available.

# Support
The best way to receive support is through the issues section of this repository. As every setup is different, support may be unable to help you, but in general we will try when we can.
If for some reason you are unable to do so, emailing us at [code@hullseals.space](mailto:code@hullseals.space) will also reach the same team.

If you are a member of the Hull Seals, please file a ticket [here](https://hullseals.space/support) instead.

# Roadmap
The project has now entered a preparatory state in which several more utility functions will be added, and core frameworks made future-proof, before
work on the long awaited Dispatch Board project can finally begin.

As always, bugfixes, speed, and stability updates are priorities as discovered, as well as general enhancements over time.

# Contributing
Interested in joining the Hull Seals Cyberseals? Read up on [the Welcome Board](https://gitlab.com/hull-seals/welcome-to-the-hull-seals-devops-board).

# Authors and Acknowledgements
Project developers:

* [Rik Overveld](https://gitlab.com/rik079)
* [David Sangrey](https://gitlab.com/Rixxan) (Responsible Cyberseal Manager)
* [Feliksas](https://gitlab.com/feliksas)
* [Ned Stevenson](https://gitlab.com/stuntphish)

Many thanks to all of our [Contributors](https://gitlab.com/hull-seals/welcome-to-the-hull-seals-devops-board/blob/master/CONTRIBUTORS.md).

# License
This project is governed under the [GNU General Public License v3.0](LICENSE) license.

# Project Status
The bot is running v1.5.2 in production, but still under active development.

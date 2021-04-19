# HalpyBOT 1.4
This is the repository for HalpyBOT, the Hull Seals IRC Chatbot Assistant.

# Description
This repository houses all of the files required to build and host your own version of the Hull Seals IRC Chat Assistant, known to us as HalpyBOT. The system is how we manage cases, recite prepared instructions for Clients and Seals, and monitor our IRC network - all in one convenient bot.

This bot is in ACTIVE DEVELOPMENT, with many core features not yet implemented.

# Installation

## Requirements
- Python 3.5+
- Asyncio Python Library
- Pydle Python Library
- Pure-SASL Python Library
- MySQL Python Library
- NumPy Python Library
- Requests Python Library
- Pytest Python Library  
- Boto3 Python Library

## Usage
To install, download the latest [release](https://gitlab.com/hull-seals-cyberseals/irc/halpybot/-/tags) from our repository. Upload and extract the files to the directory or subdirectory you wish to install from, and create your own config.py to fit your server, following the example config file provided.

## Troubleshooting
- Upon installation, be sure to replace the information in config.py to match your own details.
- Additionally, be sure to create a user account and SASL credentials for your IRC user.
- One of the most common sources of issues is your TLS settings in the bot - check these!
- If you are having issues, look through the closed bug reports.
- If no issue is similar, open a new bug report. Be sure to be detailed.
- The notification module will not load if no Amazon Web Services config data is provided.
The bot will run just fine without these, but staff notification functions will not be available.

# Support
The best way to receive support is through the issues section of this repository. As every setup is different, support may be unable to help you, but in general we will try when we can.
If for some reason you are unable to do so, emailing us at Code[at]hullseals[dot]space will also reach the same team.

# Roadmap
In the short term, the main priorities are to add more functions for the fact module, build a better command handling framework, and a reverse API for the client webhook
Later down the line, we hope to expand the functionality of HalpyBOT to be a fully functional IRC assistant for our Seals.

As always, bugfixes, speed, and stability updates are priorities as discovered, as well as general enhancements over time.

# Contributing
Interested in joining the Hull Seals Cyberseals? Read up on [the Welcome Board](https://gitlab.com/hull-seals/welcome-to-the-hull-seals-devops-board).

# Authors and Acknowledgements
The majority of this code was written by [David Sangrey](https://gitlab.com/Rixxan), [Rik Overveld](https://gitlab.com/rik079) and [Feliksas](https://gitlab.com/feliksas)

Many thanks to all of our [Contributors](https://gitlab.com/hull-seals/welcome-to-the-hull-seals-devops-board/blob/master/CONTRIBUTORS.md).

# License
This project is governed under the [GNU General Public License v3.0](LICENSE) license.

# Project Status
The bot is running v1.3.1 in production, but still under active development.

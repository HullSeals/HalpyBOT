# Contributing

Before contributing to the project, please read the general Cyberseals code of conduct 
[here](https://gitlab.com/hull-seals/welcome/-/blob/master/CONTRIBUTING.md#our-standards)

## Helping with the project

1. Contact Rixxan or Rik079 on [The Hull Seals IRC network](https://client.hullseals.space:8443/)
2. Fork the project
3. Create a new branch from `develop`
4. Write code!
5. Make sure your feature branch is up-to-date with the upstream master branch
6. Ensure you have run the unit tests for the whole project.
7. If needed, write new unit tests for your module.
8. Submit pull request

## Merge requests

- ALL merge requests MUST be reviewed by at least 1 Cyberseal team member
- Requests can only be submitted if the branch is in a FULLY working state

Make sure that the branch you're working on is up-to-date with develop.

In the merge request description, please mention the issue as `resolves #issueID` 
to automatically link the MR and the issue.

## Naming standards

### Commit messages
All commit messages must be descriptive and complete of the changes and code within.
If addressing multiple tickets, create a commit for each change and do not combine them.

It is recommended, but not absolutely required, to prefix all commit messages with the issue number if applicable.
`[HALPY-7] Create awesome function`

For commits directly to 'develop' without an associated issue, please use the following tags:

`[Minor] For a really minor addition`

`[Fix] For a minor bugfix`

`[Cleanup] after you've used the code-broom`

`[Doc] for a minor documentation change`

`[Typo] Fix typos that don't affect functioning of the bot`

### Branches
Make a feature branch off of develop using git checkout -b feature/halpy-IssueID. For other types of pull 
requests please use one of the following:

- doc - Documentation, or Documentation Update
- feature - New Features/Functionality
- fix - Bug fixes
- testing - New or updated tests.

An example of a correctly-named branch is `feature/halpy-6`

Implementations of minor functions _may_ be included in the branch of a more major function, if creating a separate
branch would be exceptionally cumbersome. Keep the guidelines for commit messages in mind.

### Merge requests names

If working from a registered issue, Include the issue name enclosed in brackets in the title of your Pull Request, ie
`[HALPY-123] Update to CONTRIBUTING.md`

Otherwise, use the type of request:

`[Doc] Make documentation even more awesome`

`[Fix] Solve issue that made bot eat rotten fish`

## Other

### Docstrings

#### Non-commands

This project uses [Google Style Python Docstrings](https://gist.github.com/redlotus/3bc387c2591e3e908c9b63b97b11d24e)for
non-commands
(functions that do not directly interact with a command handler)

#### Commands

For commands, use this simple, custom style:

```python
"""
What this command does

Usage: !primary_name <subcommand> [required argument] (optional argument)
Aliases: secondary_name
"""
```

#### Files

Files that contain any meaningful code (use your own judgement here)
have to start with a docstring of the following format:

```python
"""
file_name.py - One-sentence description of what this file does.

Copyright (c) The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md
"""
```

if the file makes use of licensed material, you must comply with all copyright
and license notice requirements listed in the license of said material.

### Code Style
This project follows PEP8 guidelines. We strongly encourage efforts are taken to enforce these standards, 
and encourage the use of tools like `Black` or `PyLint` to ensure compliance. 
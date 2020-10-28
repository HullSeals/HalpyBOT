# Contributing

Before contributing to the project, please read the general Cyberseals code of conduct [here](https://gitlab.com/hull-seals/welcome-to-the-hull-seals-devops-board/-/blob/master/CONTRIBUTING.md#our-standards)

## Helping with the project

1. Contact Rixxan or Rik079 on HSBC
2. Fork the project
3. Create a new branch from `master`
4. Write code!
5. Make sure your feature branch is up to date with the upstream master branch
6. Submit pull request

## Merge requests

- For team members, major merge requests have to be peer reviewed
- For external contributors, ALL merge requests have to be peer reviewed
- Requests can only be submitted if the branch is in a FULLY working state

Make sure that the branch you're working on is up to date with master.

In the requests description, please mention the issue as `resolves #issueID` to automatically link the MR and the issue.

## Naming standards

### Commit messages
Prefix all commit messages with the issue number if applicable. If addressing multiple tickets, create a commit for each change and do not combine them.

`[HALPY-7] Create awesome function`

### Branches
Make a feature branch off of master using git checkout -b feature/IssueID. For other types of pull requests please use one of the following:

- doc - Documentation, or Documentation Update
- feature - New Features/Functionality
- fix - Bug fixes
- testing - New or updated tests.

An example of a correctly branch names is `feature/halpy-6`

Implementations of minor functions _may_ be included in the branch of a more major function, if creating a seperate branch for it would be too cumbersome. Keep the guidelines for commit messages in mind.

### Merge requests names

If working from a registered issue, Include the issue name enclosed in brackets in the title of your Pull Request, ie `[HALPY-123] Update to CONTRIBUTING.md`

Otherwise, use the type of request:

`[Doc] Make documentation even more awesome`

`[Fix] Solve issue that made bot eat rotten fish`
# git-hub.py

A small git extension for github,
written in Python3 and relying on Github API v3.

## Install

clone and add this to your path.
`pip install -r requirements.txt` as well

## Usage

### create a pull request

```
git hub [--token <github-api-token>] <remote> create-pull-request [--into <master>] [--head <current branch>] [--title <title>] [--message <message>]
```

### more functionality to be added over time

## Configuration

To avoid having to pass the `--token` argument at every invokation,
you can set up the configuration (either global or local)
to contain the following entries:

```
[hub "github domain"]
	token = your token
```

The tool will to try to match the correct configuration entries with the given remote

Example:

```
[hub "github.com"]
	token = token123token123token123token123token123
[hub "github.enterprise.tld"]
	token = token123token123token123token123token123
```

## Example

```
git hub origin create-pull-request --into master --head feature/cookies -t "merging cookies" -m "hmm! cookies!!"
```

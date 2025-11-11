# Vinted scrapper

This script can be used to query Vinted in multiple ways in order to identify the best deals!

## Installation

### Dependencies 

This project needs a few dependencies to work:

```bash
    python3 -m venv .venv
    source .venv/bin/activate
    pip3 install -r requirements.txt
```

### Authentication

For now, authentication needed to interact with Vinted must be setup manually.
To do that, first duplicate the _.env.example_ file into a new _.env_ file. 
Then, populate the _AUTH_COOKIE_ variable with an auth cookie you retrieved from your Vinted account.

You can find it by following these steps:

- open Vinted and your network inspector in your browser
- refresh the page
- open the first request www.vinted.fr (or any other extension)
- scroll a bit and find the _Cookie_ header

## Usage

You can use the Makefile to launch the scrapper. 
Multiple filters will be proposed, they are similar to the ones available on Vinted website.
During executions, results matching your filters will be stored in the _results_ folder as CSVs.
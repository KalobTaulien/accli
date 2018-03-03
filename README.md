# Self Hosted Active Collab 5 CLI application.

Cli app for working with the self hosted collab api. Very unstable and prone to
breaking.

https://developers.activecollab.com/api-documentation/v1/people/users/all.html

# Getting Started

Create a config file:

```
cp example-config.json config.json
```

Edit config settings. Leave password empty if you want to be asked for it every
time you launch the cli. I'm not sure what client_name is for but it needs to
be set to authenticate against the api. The client_vendor is probably the name
of your company. Url is the full url of your active collab instance plus the
endpoint of the api e.g `https://activecollab.example.com/api/v1`.

# Features

- Tab complete on almost every single field.
- Fuzzy completion on almost every field.

## Create a time Record

- Value can accept standard '0:30' or '0.5' but also accepts an int of minutes.
  E.g '15' or '120'
- Summary can user Ctrl+x Ctrl+e to launch $EDITOR for editing the message

## List daily records
 
- Compute the daily total as well as billable/non billable hours

## List weekly records
 
- Compute the weekly total as well as billable/non billable hours

# Using pyactivecollab.py for connecting to api

Sample Script:

```
from pyactivecollab import Config, ActiveCollab
import getpass

# Load config, ensure password
config = Config()
config.load()
if not config.password:
    config.password = getpass.getpass()

ac = ActiveCollab(config)
ac.authenticate()
print(ac.get_info())
```

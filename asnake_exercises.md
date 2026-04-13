# ArchivesSnake Exercises

## Working with the low-level API

Return a list of repositories with the low-level API

```
from asnake.client import ASnakeClient

client = ASnakeClient()
repos = client.get('repositories').json()

print(repos)
```

We can even pretty print it

```
from pprint import pprint

pprint(repos)
```

Or maybe we want to iterate through all of our repositories by page and print the repo names

```
for repo in client.get_paged('repositories'):
    print(repo['name'])
```

## Working with the abstraction layer
If all we're wanting to do is this kind of read-only exploration, ArchivesSnake also has an abstraction layer. It can save us a little bit of typing!

Let's print all our existing repository names again

```
from asnake.aspace import ASpace

aspace = ASpace()
for repo in aspace.repositories:
    print(repo.name)
```

This abstraction gets handy as we dig deeper and deeper into records

```
for repo in aspace.repositories:
    for resource in repo.resources:
        print(resource.title)
```

And we aren't limited to just titles - what about all the publication statuses for resources that are in repository 2?

```
repo = aspace.repositories(2)
for resource in repo.resources:
    print(resource.publish)
```

We can also execute searches - here we search for all archival objects that have a level of subseries and return their titles

```
for repo in aspace.repositories:
    for ao in repo.search.with_params(q='primary_type:archival_object AND level:subseries'):
        print(ao.title)
```

We could even construct long strings with lots of pieces of comma-separated data:

```
for repo in aspace.repositories:
    for ao in repo.search.with_params(q='primary_type:archival_object AND level:subseries'):
        print(f"{repo.uri}, {ao.title}, {ao.level}, {ao.uri}")
```

## Beyond read-only actions
Finally, though all this read-only exploration has been useful in familiarizing us with the ASnake client, ASnake also allows us to do more than just search and return read only responses from the API.  We can also create and modify records with ASnake!  

Remember, during each of these interactions, we're authenticated in and passing along valid session credentials to the API.  ASnake hides away a bit of this drudgery, but each request is making use (where relevant) of the credentials we supplied in `.archivessnake.yml`.  Whatever permissions the user identified in `.archivessnake.yml` has, they extend to our interactions with the ArchivesSpace API via ASnake. In other words, everything we learned while using the Bruno GUI still applies here!

Let's use the ASnake client to create a new record.  We'll start with a pretty simple one - container profiles.

If you remember from Bruno, when we were updating a resource record, we did the following:

1. we issued a GET to that resource
2. copied the response body and pasted it into a text editor
3. made edits in the JSON
4. pasted that JSON into the payload of our POST request
5. sent it off.  

We're going to do essentially the same steps here.  Get data out -> modify the data -> put the data back in.

First, let's get a JSON representation of an existing container profile. This way, we'll have a handy JSON template of what a valid record looks like in ASpace.

Back in the Python REPL:

```
print(aspace.container_profiles(1).json())
```

While we could always copy/paste this into a file (we've got a blank `container_profile.json` file in this workspace already waiting for this data!), we can also just ask Python to do that for us. Let's redirect the output of this command to that empty, waiting file (opened in 'write' mode).

Just to prove we're being honest here, go ahead and open [container_profile.json](container_profile.json).  It's empty, right?

Now in the REPL:

```
with open('container_profile.json', 'w') as f:
    print(aspace.container_profiles(1), file=f)
```

Open `container_profile.json` and take a look!  

When creating a new container profile record, we really only need to ensure we're adding required fields to our new record.  Our current `container_profile.json` file includes a lot more data than we really need.  But it *does* demonstrate the proper syntax and key/value pairs for this record type, so using it as a template is quite helpful.  Go ahead and delete everything in the `container_profile.json` file, except for the following required fields (which can be confirmed in the Staff UI if you like):

- `name`
- `dimension_units`
- `extent_dimension`
- `depth`
- `height`
- `width`

If there are any errors in your JSON, our built-in linters will underline the issues with a red squiggle.  The file name will also turn red.  Hover over these underlines and you should get a tip about what is off about your JSON.  Speak up if you hit any road blocks!

Overwrite the values of 4 keys - `name`, `depth`, `height`, and `width`.  `name` can be whatever unique string you want to make it, but `depth`, `height`, and `width` will accept decimal values only. (`dimension_units` and `extent_dimension` *could* be altered here, but if you look at the Staff UI you'll see they are pulled from controlled value lists.  We'll leave these be to keep things simple this go around.)  Save your changes to `container_profile.json`.

Back in the Python REPL, let's make our first POST via ASnake.

```
import json

from asnake.client import ASnakeClient

with open('container_profile.json', 'r') as f:
    payload = json.load(f)

client = ASnakeClient()
response = client.post('/container_profiles', json=payload)

print(response.status_code)
print(response.json())
```

## In Conclusion
As you can see, there is a lot of power here to do some pretty impressive things.  But, already, the commands we are typing into this Python REPL are getting more and more verbose and tedious to draft.  We've even moved to having intermediary files like our `container_profile.json` file in the mix.  At a certain point, your work will progress beyond the power of a CLI tool and you may wish to investigate using standalone scripts to work with the API. This will be our next section.

You can close the Python REPL by clicking the "X" at the top of your REPL split screen.

# ArchivesSnake Exercises

## Working with the low-level API

Return a list of repositories with the low-level API

```
from asnake.client import ASnakeClient

client = ASnakeClient()
client.get('repositories').json()
```

We can even pretty print it

```
from pprint import pprint

repos = client.get('repositories').json()
pprint(repos)
```

Or maybe we want to through all our repositories by page and print their names

```
for repo in client.get_paged('repositories'):
    print(repo['name'])
```

## Working with the abstraction layer
If all we're wanting to do is this kind of read-only exploration, ArchivesSnake also has an abstraction layer. It can save us a little bit of typing!

Let's print all our existing repositories again

```
from asnake.aspace import ASpace

aspace = ASpace()
for repo in aspace.repositories:
    print(repo)
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
Finally, though all this read-only exploration has been useful in familiarizing us with the ASnake client, it also allows us to do more than just search and return read only responses from the API.  We can also create and modify records with ASnake!  

Remember, during each of these interactions, we're authenticated in and passing along valid session credentials to the API.  ASnake hides away a bit of this drudgery, but each request is making use (where relevant) of the credentials we supplied in `.archivessnake.yml`.  Whatever permissions the user identified in `.archivessnake.yml` has, also extend to our interactions with the ArchivesSpace API via ASnake. In other words, everything we learned while using the Bruno GUI still applies here!

Let's use the ASnake client to create a some new repositories.  This way, each one of you will have your own repository to play in as we move forward with the training.

If you remember from Bruno, when we were updating a resource record, we issued a GET to that resource, copied the response body, pasted that body into the payload of our POST request, made our edits in the JSON, and sent it away.  We're going to do basically the same here.

First, let's get the json representation of an existing repository. This way, we have a handy JSON template of what a valid repo looks like in ASpace.

Back in the Python REPL:

```
print(aspace.repositories(2).json())
```

While we could always copy/paste this into a file (we've got a blank `repository.json` file in this repository already waiting for this purpose!), we can also just ask Python to do that for us. Let's redirect the output of this command to that empty, waiting file (opened in 'write' mode).

```
with open('repository.json', 'w') as f:
    print(aspace.repositories(2), file=f)
```

Open `repository.json` and take a look!  

When creating a new repository record, we don't need nearly any of this data, but it is helpful for us to have a starting place to work from so that we make sure we get the syntax and key/value pairs correct.  Go ahead and delete everything in the `repository.json` file, except for:

- repo_code
- name
- publish

Overwrite the values of those remaining 3 keys, making them whatever unique values you want to use for your new, personal repository in our test environment.  Save your changes.

Back in the Python REPL, let's make our first POST via ASnake.

```
import json

with open('repository.json', 'r') as f:
    payload = json.load(f)

response = client.post('/repositories', json=payload)

print(response.status_code)
print(response.json())
```

## In Conclusion
As you can see, there is a lot of power here to do some pretty impressive things.  But, already, the commands we are typing into this Python REPL are getting more and more verbose and tedious to draft.  We've even moved to having intermediary files like our `repository.json` file in the mix.  At a certain point, your work will progress beyond the power of a CLI tool and you may wish to investigate using standalone scripts to work with the API. This will be our next section.

You can close the Python REPL by clicking the "X" at the top of your REPL split screen.

Statlyser
---------

Probe IPA 2017

custom regex syntax definition
------------------------------

You can specify special keywords in the regex to trigger additional logic to be executed:

Those keywords are separated into two categories:

### information

Those keywords are replaced with their meaning:

```sh
hostname      # replaced with the actual hostname (NOTE: you need to match hostname as a regex group too)
servicename   # replaced with actual servicename
```

### Logic

Those keywords will trigger additional logic to be executed:

```sh
bool          # treat current regex group as boolean
              # None      : False
              # not None  : True
```

### Example

```sh
# this regex group
hostname_servicename_bool_saslauth

# will eventually generate this statistics layout
{
  phd-mxin: {
    smtpd: {
      saslauth: {
        True: 10
        False: 20
        total: 30
      }
    }
  }
}
```

### Editing the results
You can edit the results before they get inserted into the statistics by overwritting this method in your Plugin:

```python
# where results is a dict with the results
# NOTE: the regex group names are not yet specialized (parsed)
# they are as you defined them in the _dataRegex
def _edit_results(self, results):
  pass
```

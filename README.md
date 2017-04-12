Tamandua
--------

Tamandua is an application for log file analysis and aggregation. In its current feature set it can parse log file lines and aggregate them into statistics.

It implements a plugin architecture where each plugin represents one service in a log file. A service typically is a process which logs to a log file. Plugins are designed to be easy to use, meaning that the user of Tamandua is anticipated to write more plugins for their specific use case.

### About the project name
[Tamandua](https://en.wikipedia.org/wiki/Tamandua) is a genus of anteaters with two species. The analogy is as follows: anteaters eat and digest a lot of small animals: ants and termites. This applications eats a lot of log file lines and aggregates them into statistics.

### Writing Plugins
The way data is extracted from the log file lines is with regexes. Each plugin consists of a minimum of two regexes:

**subscription regex** and **data regexes**, note that the latter is in plural, meaning that you can have multiple of them.

If the subscription regex of a plugin matches to a given log file line then this means that this plugin is responsible for extracting data from this line. (multiple plugins can subscribe to a log file line) As this regex is evaluated for every line times plugin count, it has to be very efficient and should not contain any regex groups. (As they are ignored)

The data regexes are used by the internals of a plugins to extract data from a log file line. It has to contain at least one regex group. It is recommended to write multiple data regexes: one for every kind of log file line for that specific service which the plugin subscribes to.

The group names of the data regexes define how the data is stored in the statistics using special keywords and flags: (the group names define the data structure of the statistics)

This project already consists of some plugins, so feel free to have a look.

#### Data Regex Resolution
`hostname` is resolved to the actual hostname.

`servicename` is resolved to the actual service name which is the class name of the plugin in lowercase.

`BOOL` is a flag which tells the compiler to treat the matched data as boolean: if this group is `None` then it will store `False` and if it is `not None` then it will resolve it to `True`

`_` creates nesting

#### Examples
`hostname_servicename_saslmethod` may resolves to `example-host_smtpd_saslmethod`. Lets assume that this regex group matches `PLAIN` and `LOGIN`. Then the resulting statistics data structure will look like this:

```sh
{
    example-host: {
        smtpd: {
            PLAIN: 1
            LOGIN: 1
            total: 2
        }
        total: 2
    }
}
```
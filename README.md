Tamandua
========

Tamandua is a framework for logfile analysis and aggregation.

Setup
-----
Tamandua requires:
 - python **>= 3.5**
 - MongoDB **>= 3.4** (Because: [$split](https://docs.mongodb.com/manual/reference/operator/aggregation/split/))

First you need to install the dependencies. Either you do this via a linux package manager (eg. `apt`) or you use a virtual environment. (Or install the deps globally) If you want to use a linux packages, please refer to `deployment/roles/tamandua/tasks/main.yml`.

Using a venv:
```sh
$ cd <tamandua-dir>

$ python3 -m venv ve
$ source ve/bin/activate
(ve) $ pip install -r requirements.txt
```

Usage
-----
### Parser
```sh
(ve) $ tamandua_parser  <logfile>
                        --help      # show all options
```

### Web
**NOTE:** For production, use the web-app in combination with wsgi, ssl, auth and apache2. (Or something similar)
```sh
# Run web-app in debug mode
(ve) $ tamandua_web

# open your browser and navigate to: http://localhost:8080/
```

Configuration
-------------
```sh
$ <your-fav-editor> config.json
    {
        # only gather data from following hosts:
        "limit_hosts": [
            "hostname1",
            "hostname2"
        ],

        # regex which extracts month, day, time and hostname from every logline
        "preregex": "^(?P<month>[^\\s]*?)\\s{1,2}(?P<day>[^\\s]*?)\\s(?P<time>[^\\s]*?)\\s(?P<hostname>[^\/\\s]*?)[^\\w-]+?",

        # output format, can be either 'pyobj-store' or 'json'
        "store_type": "pyobj-store",

        # path of the output
        "store_path": "mails.data"
    }
```

Extending Tamandua
==================
The following sections describe how to extend Tamandua.

Directory Layout
----------------
 - `src` contains the tamandua source code
 - `web` contains all components of the web view
 - `deployment` contains the ansible deployment
 - `plugins-available` contains all available plugins
 - `plugins-enabled` files or folder here are symlinked to `plugins-available`, tamandua will look in this directory for plugins.

Code Style
----------
```python
"""Add docstrings to the module."""

# Class coding style

class UpperCamelCase():
    """Supply classes with docstrings."""

    def __private_method() -> None:
        pass

    def _protected_method() -> None:
        pass

    def public_method() -> None:
        pass

    def __init__(self):
        self.__privateField
        self._protectedField
        self.publicField

    # through the whole project type annotations are used
    # so please also add them in your contibution
    # https://docs.python.org/3/library/typing.html
    #
    # eg.:
    def method(s: str, i: int) -> list:
        """Always add docstrings."""
        return []

# Interface coding style

from abc import ABCMeta, abstractmethod

# all interfaces start with the letter 'I'
# in order to easily identify them
class IUpperCamelCase(metaclass=ABCMeta):
    @abstractmethod
    def method_name(self) -> None:
        pass
```

Containers
----------
Data Collection classes are containers which handle the extracted data from the plugins. Those containers may use plugins called `Processors` to delegate processing of the data. Those containers are therefore called data containers.

Each container has a `subscribedFolder` property, this property defines which data it receives. This string has to match to the folder name of the plugins which generate data for a given container. Eg.: a container whose `subscribedFolder` is equal to `example` will receive all data from plugins in following folder: `plugins-available/example/`.

To implement a new data container you need to create a new class, inherit from `src.interfaces.IDataContainer`, implement the interface and register the container in `src.containers.data_receiver.DataReceiver`. The DataReceiver will now handle the delegation of the data from the plugins to the correct container.

For Example:

First we create a new container in `src.containers.example_container`:
```python
class ExampleContainer(IDataContainer):
    @property
    def subscribedFolder(self) -> str:
        pass

    def add_fragment(self, data: dict) -> None:
        pass

    def build_final(self) -> None:
        pass

    def represent(self) -> None:
        pass
```

Then we register this container in `DataReceiver`:
```python
def __init__(self, pluginManager: 'PluginManager'):
    self.containers = []

    #                               Our new container
    #                                       v
    cs = [Statistics, MailContainer, ExampleContainer]
```

Now we are good to go! We just need to write some data collection plugins.


### Serialization
If you want to serialize your data container, you need to inherit from `src.interfaces.ISerializable` and implement the interface:

```python
class ExampleContainer(IDataContainer, ISerializable):
    ( ... )

    def get_serializable_data(self) -> object:
    """Return a serializable object."""
        pass

    ( ... )
```

The framework will now serialize your data container!

### Use Processor Plugins in a data container
You may use processor plugins in your data container by inheriting from `src.interfaces.IRequiresPlugins` and implementing the interface:

```python
class ExampleContainer(IDataContainer, IRequiresPlugins):
    ( ... )

    def set_pluginmanager(self, pluginManager: 'PluginManager') -> None:
        """Assign the pluginManager to a member field for later use."""
        self._pluginManager = pluginManager

    def build_final(self) -> None:
        """
        Then you may request some processors by their responsibility from the pluginManager.

        This is discussed in more detail in the 'Plugins' section.
        """

        chain = self._pluginManager.get_chain_with_responsibility('postprocessors')

        # construct meta object
        pd = ProcessorData(mail)

        # give data to processors
        chain.process(pd)

        # evaluate action result
        if pd.action == ProcessorAction.DELETE:
            pass

    ( ... )
```

The framework will now setup your data container with the plugin manager. (Dependency Injection)

Plugins
-------
Tamandua differentiates between two types of plugins: data collection and processor plugins. As the name suggests the first ones are used to gather data from logfiles and the second ones are used for additional data processing. (eg. postprocessing)

### Data Collection
Data collection plugins are located in folders in `plugins-available` without ending to `.d`. They may inherit from different base classes or directly from the `src.interfaces.IPlugin` interface: (It is recommended to inherit from a base class for generic plugin logic)

Lets create a new plugin:

First we have to decide to which data container we want to send the data extracted from our plugin. This is done by putting the plugin in the corresponding folder in `plugins-available/<IDataContainer.subscribedFolder>/.`.

At the time of writing this readme there are two data containers: `MailContainer` and `Statistics` which subscribe to `mail-container` and `statistics`. The plugins written for both data containers are almost the same:

#### Mail-Aggregation

```python
class ExampleDataCollection(SimplePlugin):
    def check_subscription(self, line: str) -> bool:
        pass

    def gather_data(self, line: str, preRegexMatches: dict) -> dict:
        pass
```

#### Statistics
The statistics plugin is implemented the same way as the mail aggregation plugins, the only difference is that you will want to inherit from `src.plugins.plugin_base.PluginBase` instead of `SimplePlugin`. This is because the base class `PluginBase` offers great means to extend your regexp group names.

```python
class ExampleDataCollection(PluginBase):
    def check_subscription(self, line: str) -> bool:
        pass

    def gather_data(self, line: str, preRegexMatches: dict) -> dict:
        pass
```

#### Generic data collection plugin
If you do not want to reuse any functionality of any of those base classes, you may inherit directly from the `src.interfaces.IPlugin` interface and implements its members. The pluginManager will now know how to treat your "custom" plugin.

Eg.:
```python
class CustomPlugin(IPlugin):
    def check_subscription(self, line: str) -> bool:
        pass

    def gather_data(self, line: str, preRegexMatches: dict) -> dict:
        pass
```

### Processors
The most basic Processor inherits from `src.interfaces.IProcessorPlugin`.
```python
class ExampleProcessor(IProcessorPlugin):
    def process(self, obj: object) -> None:
        pass
```

#### Processors are chained
A given type of processors are put together to a chain of responsibility by the PluginManager. Then a responsibility (string) is assigned to this chain. Clients can then get those chains by their responsibility:

Client code:
```python
chain = pluginManager.get_chain_with_responsibility('example_resp')
```

A client can then give an object to the chain which will in turn give this object to all processors in a given order.

```python
chain.process(object)
```

Processor plugins are located in plugin folders ending to `.d`. (eg. `postprocessors.d`) The name of their responsibility is this foldername minus the `.d` at the end. (eg. folder: `postprocessors.d` --> responsibility: `postprocessors`)

For each of this responsibilities a `Chain` is created.

#### Order of execution
Each `Chain` sorts its processors by the filename of the file in which their were found.

For Example:
```sh
.
└── postprocessors.d
    ├── 01_remover.py
    ├── 02_tag_delivery.py
    ├── 03_tag_action.py
    ├── 04_tag_maillinglist.py
    ├── 05_tag_spam.py
    └── 06_verify_delivery.py
```

Plugins in those folder will be executed in the order shown. Note that plugins are classes in those files, this means, that if a file contains multiple plugins, they will not have a specific order.

#### Using metadata with Processors
You may want to trigger external logic from within a processor. This is done via a wrapper class (`ProcessorData`) which holds this metadata.

For example you may want to delete a given object, this can be done as follow:
```python
class ExampleProcessor(IProcessorPlugin):
    def process(self, obj: ProcessorData) -> None:
        obj.action = ProcessorAction.DELETE
```

The `Chain` will detect, that a given plugin has marked its data to be deleted. So it will stop iterating over its processor and give control back to the caller immediately. (Who then will do the actual deletion)

### Introduce a new type of plugin
If a new type of plugins are required, then the internals of `src.plugins.plugin_manager.PluginManager` have to be adapted. Every plugin has to inherit from the marker interface `src.interfaces.IAbstractPlugin`. Classes of this type are detected by the PluginManager as plugins. After all those plugins are loaded you have to decide what to do with them. Data collection plugins inherit from `IPlugin` and Processors inherit from `IProcessorPlugin`, so you need to create a new interface for the new plugin type, eg. `IExamplePlugin` and tell the PluginManager what to do with those plugins.

Appendix
========
## Project Name
[Tamandua](https://en.wikipedia.org/wiki/Tamandua) is a genus of anteaters with two species. The analogy is as follows: anteaters eat and digest a lot of small animals: ants and termites. This applications eats a lot of log file lines and aggregates them into statistics.

## System Requirements
Tamandua consumes a lot of RAM, so plan accordingly. (memusage: > 2x size of logfile)

```sh
-rw-r----- 1 amartako amartako 264M Jun 14 12:09 /ashscr1/jupyter/mail.log-20170613

amartako@ash:~/Documents/Projects/IPA/Tamandua (master)$ /usr/bin/time -v ./tamandua_parser.py /ashscr1/jupyter/mail.log-20170613 --no-print
	Command being timed: "./tamandua_parser.py /ashscr1/jupyter/mail.log-20170613 --no-print"
	User time (seconds): 113.74
	System time (seconds): 1.23
	Percent of CPU this job got: 94%
	Elapsed (wall clock) time (h:mm:ss or m:ss): 2:02.20
	Average shared text size (kbytes): 0
	Average unshared data size (kbytes): 0
	Average stack size (kbytes): 0
	Average total size (kbytes): 0
	Maximum resident set size (kbytes): 593768       <--------
	Average resident set size (kbytes): 0
	Major (requiring I/O) page faults: 0
	Minor (reclaiming a frame) page faults: 189591
	Voluntary context switches: 4390
	Involuntary context switches: 396
	Swaps: 0
	File system inputs: 539720
	File system outputs: 152672
	Socket messages sent: 0
	Socket messages received: 0
	Signals delivered: 0
	Page size (bytes): 4096
	Exit status: 0
```

## Windows support
Tamandua has full Windows support.

The only thing you need to pay attention on Windows is, that linux symlinks won't work. This means that the plugins have to go into the `plugins-enabled` folder by another mean.

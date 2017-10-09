Tamandua
========

Tamandua is a framework for logfile analysis and aggregation developed at and for the [IT Services Group D-PHYS](https://nic.phys.ethz.ch/) (called _ISG_ in this readme) located at the [ETH Zurich](https://www.ethz.ch/en.html).

The ISG is running a complex mail infrastructure. It consists out of four different servers, where each server is responsible for another task. Each server generates logfiles about different actions performed. This log is consolidated on a fifth server, called the loghost. The goal of Tamandua is to take the consolidated logfile, parse it, extract information and aggregate this information into so-called mail-objects.  
Each mail-object represents one mail processed by the infrastructure. This information serves two purposes: statistics are generated to provide the system administrators at the ISG with an overview of the current mail flow. Secondly, the mail objects can be searched in order to comprehend and resolve errors. (for example false positives in the virus and spam filter) This search function is also used to help customers (mainly ETH intern) to resolve problems, for example, when a mail "went missing" or when "a mail wasn't delivered".

Tamandua was specifically designed and developed for the ISG. This means that Tamandua contains domain-specific parts and will probably not work out of the box in another environment. Although it can be adapted easily to operate in any other environment.

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
## Table of contents

  - [Setup](#setup)
  - [Usage](#usage)
    - [Manager](#manager)
    - [Parser](#parser)
    - [Web](#web)
  - [Docs](#docs)
  - [Deployment](#deployment)
  - [Configuration](#configuration)
- [Extending Tamandua](#extending-tamandua)
  - [Directory Layout](#directory-layout)
  - [Code Style](#code-style)
  - [Components](#components)
    - [Parser](#parser-1)
    - [Web-App](#web-app)
  - [Plugins](#plugins)
    - [Data Collection](#data-collection)
      - [Mail-Aggregation](#mail-aggregation)
      - [Statistics](#statistics)
      - [Generic data collection plugin](#generic-data-collection-plugin)
    - [Processors](#processors)
      - [Processors are chained](#processors-are-chained)
      - [Order of execution](#order-of-execution)
      - [Using metadata with Processors](#using-metadata-with-processors)
    - [Containers](#containers)
      - [Use a repository within a container](#use-a-repository-within-a-container)
      - [Use Processor Plugins in a data container](#use-processor-plugins-in-a-data-container)
    - [Introduce a new type of plugin](#introduce-a-new-type-of-plugin)
  - [Expressions](#expressions)
  - [Countable Iterables](#countable-iterables)
  - [Repository](#repository)
- [Authors](#authors)
- [License](#license)
- [Appendix](#appendix)
  - [Project Name](#project-name)
  - [State of this documentation](#state-of-this-documentation)
  - [Domain specific parts](#domain-specific-parts)
  - [System Requirements](#system-requirements)
  - [Windows support](#windows-support)
  - [Concrete](#concrete)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

Setup
-----

Tamandua requires:

- python **>= 3.5** (Because: [type hints](https://docs.python.org/3/library/typing.html))
- MongoDB **>= 3.4** (Because: [$split](https://docs.mongodb.com/manual/reference/operator/aggregation/split/))

First you need to install the dependencies. You do this either via a linux package manager (eg. `apt`) or you use a virtual environment. (Or install the deps globally) If you want to use a linux packages, please refer to `deployment/roles/tamandua/tasks/main.yml`.

Using a `virtualenv`:

```sh
$ cd <tamandua-dir>

$ python3 -m venv ve
$ source ve/bin/activate
(ve) $ pip install -r requirements.txt
```

Usage
-----

### Manager

The manager encapsulated the parser and associated administrative tasks. In almost all cases you will use the manager.

Most commonly used options:
```sh
(ve) $ tamandua_manager  --help             # show all CLI options with description
                    run                     # run the parser pipeline:
                                            # get logfile diff --> run parser --> cleanup --> remove local temp data
                    cleanup                 # remove data which is older than 30 days (default)
```

### Parser

```sh
(ve) $ tamandua_parser  <logfile>
                        --print-data        # print data after aggregation (eg. mail objects)
                        --print-msgs        # print system messages (eg. number of currently processed lines or aggregated objects)
                        --help              # show all options
```

### Web

**NOTE:** For production, use the web-app in combination with wsgi, **ssl**, **auth** and `apache2`. (Or something similar)

```sh
# Run web-app in debug mode
(ve) $ tamandua_web

# open your browser and navigate to: http://localhost:8080/
```

Docs
----

Generate ToC:

```sh
$ doctoc --title '## Table of contents' --github README.md
```

Although you first need to install `doctoc`:
```sh
$ npm install -g doctoc
```

Deployment
----------

[Ansible](https://www.ansible.com/) is used to automate the deployment.

Run the deployment:
```sh
$ cd deployment
$ ansible-playbook tamandua_deployment.yml
```

For more information, consider looking at the `tamandua` role.

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

        # specify database type
        "database_type": "mongo",

        #
        # All options from this point on vary depending on the database_type
        # This options here are for mongodb (currently only mongodb is supported)
        #

        # name of the database to store the data
        "database_name": "tamandua",

        # name of the collection containing the complete data
        "collection_complete": "complete",

        # and the incomplete data
        "collection_incomplete": "incomplete",

        # name of the collection of the metadata
        "collection_metadata": "metadata",

        # servername/ip
        "dbserver": "localhost",

        # port
        "dbport": 27017
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
    # in order to keep tamandua typesafe, _always_ use them
    # https://docs.python.org/3/library/typing.html
    #
    # eg.:
    def method(s: str, i: int) -> List[Union[str, int]]:
        """Always add docstrings."""
        return [s, i]

# Interface coding style

from abc import ABCMeta, abstractmethod

# all interfaces start with the letter 'I'
# in order to easily identify them
class IUpperCamelCase(metaclass=ABCMeta):
    @abstractmethod
    def method_name(self) -> None:
        pass

    @property
    @abstractmethod
    def property(self):
        return 'foobar'
```

Modules and packages: (snake case)

```sh
package_name/module_name.py
```

Components
----------

Tamandua consists of 2 main components: the parser which extracts and aggregates data from a given logfile and the web-app which represents this gathered data to the user. Each of those two components is further divided into internal components.

The parser will store the processed data in a database which is also used by the web-app. This database is abstracted using the [repository pattern](https://msdn.microsoft.com/en-us/library/ff649690.aspx). (More to it later)

### Parser

The parser consists of:

- PluginManager
  - Plugins
    - Containers
    - Data Extraction
    - Processors (pre/post/edge cases)
- Repository
  - MongoDB

Data flow:
```sh
logfile --> logline --> pluginmanager --> data extraction --> containers --> pre/post/edge case processors --> repository --> store data to disk
```

### Web-App

The web-app follows the design principle of [MVC](https://en.wikipedia.org/wiki/Model%E2%80%93view%E2%80%93controller):

- Controller, Model runs on the server
- View run in the browser of the user

User searches data:

```sh
view search form --> controller --> repository --> get data from database --> controller --> return results to view
```

Plugins
-------

Available plugins are found in the `plugins-available` folder and enabled plugins are symlinked into the `plugins-enabled` folder.

### Data Collection

Data collection plugins are located in folders in `plugins-available`. They may inherit from different base classes or directly from the `IPlugin` interface: (It is recommended to inherit from a base class for generic plugin logic)

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

If you do not want to reuse any functionality of any of those base classes, you may inherit directly from the `IPlugin` interface and implements its members. The pluginManager will now know how to treat your "custom" plugin.

Eg.:
```python
class CustomPlugin(IPlugin):
    def check_subscription(self, line: str) -> bool:
        pass

    def gather_data(self, line: str, preRegexMatches: dict) -> dict:
        pass
```

### Processors

The most basic Processor inherits from `IProcessorPlugin`.

```python
class ExampleProcessor(IProcessorPlugin):
    def process(self, obj: object) -> None:
        pass
```

#### Processors are chained

A given type of processors are put together to a chain of responsibility by a concrete `IPluginCollection`. Then a responsibility (string) is assigned to this chain. Clients can then get those chains by their responsibility:

Client code:
```python
chain = pluginManager.get_chain_with_responsibility('example_resp')
```

A client can then give an object to the chain which will in turn give this object to all processors in a given order.

```python
chain.process(object)
```

Processor plugins are located in plugin folders under `plugins-available`. (eg. `postprocessors.d`) The name of their responsibility is this foldername minus the `.d` at the end. (eg. folder: `postprocessors.d` --> responsibility: `postprocessors`) Although the `.d` is not required.

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

### Containers

Container plugins are plugins which process the data extracted using the data extraction plugins. Currently there are two container plugins: `Statistics` which is not used and `MailContainer` which aggregates loglines into mail objects.

To implement a new container you need to implement the `IDataContainer` interface:

First we create a new container in `src.containers.example_container`:
```python
class ExampleContainer(IDataContainer):
    ( ... )
```

#### Use a repository within a container

Implement the `IRequiresRepository` interface and you will be given a repository by the framework. (DI)

```python
class MailContainer(IDataContainer, IRequiresRepository):
    def set_repository(self, repository: IRepository) -> None:
        # called when constructing this contaier
        # store the given repository in a member field
        self._repository = repository
```

You may now use the repository to save/get data.

#### Use Processor Plugins in a data container

You may use processor plugins in your data container by inheriting from `IRequiresPlugins` and implementing the interface:

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

### Introduce a new type of plugin

You may add a new type of plugin:

Every plugin has to inherit from the marker interface `IAbstractPlugin` in order to be detected as plugin by the plugin manager.

A plugin is defined by its interface:

```python
from abc import ABCMeta

class IMyNewPlugin(IAbstractPlugin):
    """"""

    @abstractmethod
    def do_something(self):
        """"""
        pass
```

Then you need to implement a new plugin collection: (`src.plugins.plugin_collection`)

```python
class MyNewPluginCollection(BasePluginCollection):
    """""""
    @property
    def subscribed_cls(self) -> type:
        # subscribe to your new type of plugin
        # in order to receive those plugins
        # from the PluginAssociator
        return IMyNewPlugin
```

And register this new plugin collection to the `PluginAssociator`: (`src.plugins.plugin_collection`)

```python
class PluginAssociator():
    """Associate a given plugin with a plugin collection."""

    def __init__(self, pluginManager: 'PluginManager'):
        """Constructor of PluginAssociator."""

        # List[IPluginCollection]
        self._pluginCollections = [
            ContainerPluginCollection(pluginManager),
            DataCollectionPlugins(),
            ProcessorPluginCollection(),

            # add your new collection here
            MyNewPluginCollection()
        ]
```

Expressions
-----------

In order to abstract the query language of each concrete repository (eg. MongoDB and MySQL) Tamandua has its own intermediate query language. (aka intermediate expression) This query language is used extensively throughout the project. (`View --> Controller --> Repository`, `Parser --> Repository`) Each concrete repository then has to compile this intermediate expression to its specific query language.

In order to abstract the expression itself and make building expressions easier an `ExpressionBuilder` was implemented:

```python
from src.expression.builder import ExpressionBuilder, ExpressionField, Comparator

builder = ExpressionBuilder()
builder.add_field(
    ExpressionField('field', 'value', Comparator(Comparator.regex_i))
)

# check source for more methods (eg. adding datetime)
```

As you can see an `ExpressionField` and a `Comparator` are used to further abstract the components of an expression.

An `ExpressionField` represents a field you want to search for. A `Comparator` is, well, a comparator, checkout source for all options.

See also [builder pattern](https://sourcemaking.com/design_patterns/builder).

Countable Iterables
-------------------

Inspired by: [.NET's IEnumerable.Count](https://msdn.microsoft.com/en-us/library/bb338038(v=vs.110).aspx)

Repository
----------

Tamandua abstract the storage backend using a repository pattern. This allows the developer to easily extend Tamandua with a new storage backend. The creation of this repository is handled by a `RepositoryFactory`.

Lets assume that Tamandua should be changed so that it writes its data to a couchbase db. For this we will first create a new concrete repository:

Each repository has to implement the `IRepository` interface:

```python
from src.repository.interfaces import IRepository

class CouchbaseRepository(IRepository):
    ( ... )
    # Look at docstrings in interface source for implementation details
```

Then we will need to add the new repository to the `RepositoryFactory`:

```python
class RepositoryFactory():

    __repo_map = {
        # the existing mongo repository
        'mongo': {
            'config': MongoRepository.get_config_fields(),
            'cls': MongoRepository
        }

        # the new couchbase repository
        'couchbase': {
            'config': CouchbaseRepository.get_config_fields(),
            'cls': CouchbaseRepository
        }
    }

    ( ... )
```

Now its time to change the database type in the config file in order for the framework to actually use the new repository:

```json
{
    "database_type": "couchbase"
}
```

Note, that the `database_type` field has to match the key in the `__repo_map`.

See also [repository pattern](https://msdn.microsoft.com/en-us/library/ff649690.aspx), [factory method](https://sourcemaking.com/design_patterns/factory_method).

Authors
=======

- Anastassios Martakos

License
=======

```
Tamandua - Logfile aggregation framework
Copyright (C) 2017  Anastassios Martakos

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
```

Appendix
========

## Project Name

[Tamandua](https://en.wikipedia.org/wiki/Tamandua) is a genus of anteaters with two species. The analogy is as follows: anteaters eat and digest a lot of small animals: ants and termites. This applications eats a lot of log file lines and aggregates them into statistics.

## State of this documentation

This readme still lacks a lot of explanations. (Especially the description of components that are domain specific and how to rewrite them to a more generic state or to your environment.) Although docstrings are provided through the whole source code. Please refer to them.

The documentation will, by any chance, be completed someday.

## Domain specific parts

Tamandua is developed at ETH Zurich Department Physics in the ISG group. ([IT Services Group D-PHYS](https://nic.phys.ethz.ch/)) It's goal is to provide the system administrators there with an easy way to analyse the mail traffic of their mail infrastructure. This means that Tamandua contains some domain specific parts like the hostnames of the mail servers. Although Tamandua can be easily rewritten to operate in a different environment.

## System Requirements

Refer to the [Performance Measurements (incomplete)](docs/perf_messurements.md)

Generally speaking consumes the parser a bit more RAM than the size of the logfile:

```sh
130MB logfile --> 160 MB RAM usage
```

Note that MongoDB can use up to several hundred MB RAM when it is building its indexes.

## Windows support

Tamandua has full Windows support.

The only thing you need to pay attention on Windows is, that linux symlinks won't work out of the box. You need to install git for windows and either enable symlinks during the installation or enable them when you clone the repo:

```sh
$ git clone -c core.symlinks=true <URL>
```

Although in order to make the actual symlinks you need to have admin rights.

[More info on this topic](https://github.com/git-for-windows/git/wiki/Symbolic-Links)

Git GUIs like GitKraken also seems to have problems working with symlinks on windows. (You may use the powershell instead)

## Concrete

[In this context not cement.](https://en.wikipedia.org/wiki/Class_(computer_programming)#Abstract_and_concrete)

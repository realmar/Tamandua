"""DataReceiver receives extracted data from logfiles and distributes them between IDataContainers."""

from typing import List

from ..plugins.interfaces import IDataContainer
from ..exceptions import print_warning


class DataReceiver():
    """Distribute extracted data from the loglines between data containers."""

    def __init__(self, containers: List[IDataContainer]):
        self.containers = containers

    def get_conainers_of_type(self, t: type) -> list:
        """Get a list of containers of a specific type."""
        filtered = []

        for container in self.containers:
            if isinstance(container, t):
                filtered.append(container)

        return filtered

    def add_info(self, folderToData: dict) -> None:
        """
        Add some data to the containers.
        
        This method uses the subscribedFolder field of the containers
        to determine to which container it should give the data.
        """
        for folder, data in folderToData.items():
            foundContainer = False
            for container in self.containers:
                if folder == container.subscribedFolder:
                    container.add_fragment(data)
                    foundContainer = True
                    break

            if not foundContainer:
                print_warning('Did not find matching data container for identifier: ' + folder)

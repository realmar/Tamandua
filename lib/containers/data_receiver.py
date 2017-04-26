"""DataReceiver receives extracted data from logfiles and distributes them between IDataContainers."""


from .statistics import Statistics
from .mail_container import MailContainer

class DataReceiver():
    def __init__(self):
        self.containers = [
            Statistics(),
            MailContainer()
        ]

    def get_conainers_of_type(self, t: type) -> list:
        filtered = []

        for container in self.containers:
            if isinstance(container, t):
                filtered.append(container)

        return filtered

    def add_info(self, folderToData: dict) -> None:
        for folder, data in folderToData.items():
            for container in self.containers:
                if folder == container.subscribedFolder:
                    container.add_info(data)
                    break
"""Here are the statistics composed and stored."""

from pprint import pprint


class Statistic():
    """Container which composes and holds the statistics."""

    def __init__(self):
        """Ctor of Statistic."""
        self.data = {}

    def add_info(self, data):
        """Add more data to the statistic."""
        for name, value in data.items():
            separateNames = name.split('_')
            currLayer = self.data
            currIteration = 0

            for subname in separateNames:
                currIteration += 1
                if currLayer.get(subname) is None:
                    if len(separateNames) == currIteration:
                        currLayer[subname] = {value: 1}
                        break
                    else:
                        currLayer[subname] = {}
                        currLayer = currLayer[subname]
                else:
                    if len(separateNames) == currIteration:
                        if currLayer[subname].get(value) is None:
                            currLayer[subname][value] = 1
                        else:
                            currLayer[subname][value] += 1
                        break
                    else:
                        currLayer = currLayer[subname]

    def represent(self):
        """Output the statistic to STDOUT."""
        pprint(self.data)

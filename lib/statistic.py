"""Here are the statistics composed and stored."""

from pprint import pprint


class Statistic():
    """Container which composes and holds the statistics."""

    def __init__(self):
        """Ctor of Statistic."""
        self.data = {}

    def add_info(self, data):
        """Add more data to the statistic."""
        for name, value in data:
            separateNames = name.split('_')
            currLayer = self.data
            currIteration = 0

            for name in separateNames:
                currIteration += 1

                if currLayer.get(name) is None:
                    if len(separateNames) == currLayer:
                        currLayer[name] = 1
                        break
                    else:
                        currLayer[name] = {}
                        currLayer = currLayer[name]
                else:
                    if len(separateNames) == currLayer:
                        currLayer[name] += 1
                        break
                    else:
                        currLayer = currLayer[name]

    def represent(self):
        """Output the statistic to STDOUT."""
        pprint(self.data)

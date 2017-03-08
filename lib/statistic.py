"""Here are the statistics composed and stored."""

from pprint import pprint


class Statistic():
    """Container which composes and holds the statistics."""

    def __init__(self):
        """Ctor of Statistic."""
        self.data = {'totalentries': 0}

    def __calculate_rest(self):
        """Add the remainder of total to the statistics."""


    def add_info(self, d):
        """Add more data to the statistic."""
        for data in d:
            for name, value in data.items():
                separateNames = name.split('_')
                currLayer = self.data
                currIteration = 0

                for subname in separateNames:
                    currIteration += 1
                    if currLayer.get(subname) is None:
                        if len(separateNames) == currIteration:
                            currLayer[subname] = {value: 1, 'total': 1}
                            break
                        else:
                            currLayer[subname] = {}
                            currLayer[subname]['total'] = 1
                            currLayer = currLayer[subname]
                    else:
                        if len(separateNames) == currIteration:
                            if currLayer[subname].get(value) is None:
                                currLayer[subname][value] = 1
                            else:
                                currLayer[subname][value] += 1
                            currLayer[subname]['total'] += 1
                            break
                        else:
                            currLayer[subname]['total'] += 1
                            currLayer = currLayer[subname]
        if len(d) > 0:
            self.data['totalentries'] += 1

        self.__calculate_rest()

    def represent(self):
        """Output the statistic to STDOUT."""
        pprint(self.data)

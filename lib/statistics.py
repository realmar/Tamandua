"""Here are the statistics composed and stored."""

from pprint import pprint
from .exceptions import MultipleDataSetsUnknown


class Statistics():
    """Container which composes and holds the statistics."""

    def __init__(self):
        """Constructor of Statistic."""
        self.data = {
            'total_relevant': 0,
            'total_irrelevant': 0,
            'total': 0,
            'total_unknown': 0
            }

    def add_info(self, d):
        """Add more data to the statistic."""
        lineHasData = False
        setHasData = True

        for hasData, data in d:
            if not hasData:
                if len(data) > 1:
                    raise MultipleDataSetsUnknown(self.__class__.__name__)

                setHasData = False

            for key, value in data.items():
                def incrementValue(cl):
                    if cl.get(value) is None:
                        cl[value] = 1
                    else:
                        cl[value] += 1

                separateNames = key.split('_')
                currLayer = self.data
                currIteration = 0

                def isLast():
                    return len(separateNames) == currIteration

                if value is not None:
                    lineHasData = True
                else:
                    # if the value we want to add is None
                    # then we ignore it and continue with the next
                    continue


                for subname in separateNames:
                    currIteration += 1

                    if currIteration > 1:
                        currLayer['total'] += 1
                        if not hasData:
                            incrementValue(currLayer)

                    if currLayer.get(subname) is None:
                        v = 0
                        if isLast():
                            v = 1

                        tmp = {'total': v}

                        if not hasData or isLast():
                            tmp[value] = v

                        currLayer[subname] = tmp

                        if isLast():
                            break

                    if isLast():
                        currLayer[subname]['total'] += 1
                        incrementValue(currLayer[subname])
                        break

                    currLayer = currLayer[subname]

        if len(d) > 0:
            self.data['total_relevant'] += 1

        if (not lineHasData or not setHasData) and len(d) > 0:
            self.data['total_unknown'] += 1

        self.data['total'] += 1
        self.data['total_irrelevant'] = self.data['total'] - self.data['total_relevant']

    def represent(self):
        """Output the statistics to STDOUT."""
        pprint(self.data)

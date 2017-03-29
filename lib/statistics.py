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
                separateNames = key.split('_')
                currLayer = self.data
                currIteration = 0

                if value is not None:
                    lineHasData = True

                for subname in separateNames:
                    currIteration += 1
                    if currLayer.get(subname) is None:
                            tmp = {'total': 1}
                            if not hasData or len(separateNames) == currIteration:
                                tmp[value] = 1
                            currLayer[subname] = tmp
                            currLayer = currLayer[subname]
                    else:
                        def incrementValue(cl):
                            if cl.get(value) is None:
                                cl[value] = 1
                            else:
                                cl[value] += 1

                        if currIteration > 1:
                            currLayer['total'] += 1
                            if not hasData:
                                incrementValue(currLayer)

                        if len(separateNames) == currIteration:
                            currLayer[subname]['total'] += 1
                            incrementValue(currLayer[subname])

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

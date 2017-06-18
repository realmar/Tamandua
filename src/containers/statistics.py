"""Here are the statistics composed and stored."""

from pprint import pprint
from ..exceptions import MultipleDataSetsUnknown
from ..interfaces import IDataContainer


class Statistics(IDataContainer):
    """Container which composes and holds the statistics."""

    def __init__(self):
        """Constructor of Statistic."""
        self._data = {
            'total_relevant': 0,
            'total_irrelevant': 0,
            'total': 0,
            'total_unknown': 0
        }

    @property
    def subscribedFolder(self) -> str:
        return "statistics"

    def add_fragment(self, data: dict) -> None:
        """Add more data to the statistic."""
        lineHasData = False
        setHasData = True

        for hasData, flags, d in data['data']:
            if not hasData:
                if len(d) > 1:
                    raise MultipleDataSetsUnknown(self.__class__.__name__)

                setHasData = False

            for key, value in d.items():
                def increment_value(cl):
                    if cl.get(value) is None:
                        cl[value] = 1
                    else:
                        cl[value] += 1

                separateNames = key.split('_')
                currLayer = self._data
                currIteration = 0

                def is_last():
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
                            increment_value(currLayer)

                    if currLayer.get(subname) is None:
                        v = 0
                        if is_last():
                            v = 1

                        tmp = {'total': v}

                        if not hasData or is_last():
                            tmp[value] = v

                        currLayer[subname] = tmp

                        if is_last():
                            break

                    if is_last():
                        currLayer[subname]['total'] += 1
                        increment_value(currLayer[subname])
                        break

                    currLayer = currLayer[subname]

        if len(data) > 0:
            self._data['total_relevant'] += 1

        if (not lineHasData or not setHasData) and len(data) > 0:
            self._data['total_unknown'] += 1

        self._data['total'] += 1
        self._data['total_irrelevant'] = self._data['total'] - self._data['total_relevant']

    def build_final(self) -> None:
        """Does nothing ATM, needed for interface."""
        pass

    def represent(self) -> None:
        """Output the statistics to STDOUT."""
        pprint(self._data)

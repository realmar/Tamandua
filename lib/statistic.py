"""Here are the statistics composed and stored."""

from pprint import pprint


class Statistic():
    """Container which composes and holds the statistics."""

    def __init__(self):
        """Ctor of Statistic."""
        self.data = {
            'totalrelevant': 0,
            'totalnonrelevant': 0,
            'totallines': 0,
            'totalunknown': 0
            }

    def increment_line_count(self):
        self.data['totallines'] += 1
        self.data['totalnonrelevant'] = self.data['totallines'] - self.data['totalrelevant']

    def add_info(self, d):
        """Add more data to the statistic."""
        lineHasData = False

        for data in d:
            hasData = False
            dictKeyChain = next(iter(data.keys())).split('_')[:-1]

            for name, value in data.items():
                separateNames = name.split('_')
                currLayer = self.data
                currIteration = 0

                for subname in separateNames:
                    currIteration += 1
                    if currLayer.get(subname) is None:
                        if len(separateNames) == currIteration:
                            if value is not None:
                                lineHasData = True
                                hasData = True

                                currLayer[subname] = {value: 1, 'total': 1}

                            break
                        else:
                            currLayer[subname] = {}
                            currLayer = currLayer[subname]
                    else:
                        if len(separateNames) == currIteration:
                            if value is not None:
                                lineHasData = True
                                hasData = True

                                if currLayer[subname].get(value) is None:
                                    currLayer[subname][value] = 1
                                else:
                                    currLayer[subname][value] += 1

                                currLayer[subname]['total'] += 1

                            break
                        else:
                            currLayer = currLayer[subname]

            currLayer = self.data
            for key in dictKeyChain:
                currLayer = currLayer[key]

                if currLayer.get('total') is None:
                    currLayer['total'] = 1
                else:
                    currLayer['total'] += 1

                if not hasData:
                    if currLayer.get('unknown') is None:
                        currLayer['unknown'] = 1
                    else:
                        currLayer['unknown'] += 1

        if len(d) > 0:
            self.data['totalrelevant'] += 1

        if not lineHasData and len(d) > 0:
            self.data['totalunknown'] += 1

    def represent(self):
        """Output the statistic to STDOUT."""
        pprint(self.data)

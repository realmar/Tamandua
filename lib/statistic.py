"""Here are the statistics composed and stored."""

from pprint import pprint


class Statistic():
    """Container which composes and holds the statistics."""

    def __init__(self):
        """Ctor of Statistic."""
        self.data = {
            'totalrelevant': 0,
            'totallines': 0,
            'totalunknown': 0
            }

    def increment_line_count(self):
        self.data['totallines'] += 1
        self.data['totalunknown'] = self.data['totallines'] - self.data['totalrelevant']

    def add_info(self, d):
        """Add more data to the statistic."""
        lineIsRelevant = False

        for data in d:
            for name, value in data.items():
                separateNames = name.split('_')
                currLayer = self.data
                currIteration = 0

                for subname in separateNames:
                    currIteration += 1
                    if currLayer.get(subname) is None:
                        if len(separateNames) == currIteration:
                            if value is None:
                                value = 'unknown'
                            else:
                                lineIsRelevant = True

                            currLayer[subname] = {value: 1, 'total': 1}
                            break
                        else:
                            currLayer[subname] = {}
                            currLayer[subname]['total'] = 1
                            currLayer = currLayer[subname]
                    else:
                        if len(separateNames) == currIteration:
                            if value is None:
                                value = 'unknown'
                            else:
                                lineIsRelevant = True

                            if currLayer[subname].get(value) is None:
                                currLayer[subname][value] = 1
                            else:
                                currLayer[subname][value] += 1
                            currLayer[subname]['total'] += 1
                            break
                        else:
                            currLayer[subname]['total'] += 1
                            currLayer = currLayer[subname]
        if len(d) > 0 and lineIsRelevant:
            self.data['totalrelevant'] += 1

    def represent(self):
        """Output the statistic to STDOUT."""
        pprint(self.data)

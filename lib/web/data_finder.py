from datetime import datetime

from ..serialization.serializer import Serializer
from .. import constants


class DataFinder():
    def __init__(self, config) -> None:
        self._config = config
        self._data = []
        self.availableFields = []

        self.load_data()

    def load_data(self):
        self._data = Serializer(self._config).load()['MailContainer']
        self.analise_data()

    def analise_data(self) -> None:
        """
        Analise the data.
        
        This will generate the availableFields. This method is called from load_data.
        """

        tmpAvailableFields = {}

        def inner_analise(data):
            for key, value in data.items():
                if tmpAvailableFields.get(key) is None:
                    tmpAvailableFields[key] = True

        for data in self._data:
            if isinstance(data, list):
                for d in data:
                    inner_analise(d)
            else:
                inner_analise(data)

        self.availableFields = sorted(tmpAvailableFields.keys())


    def get_all(self) -> list:
        return self._data

    def get_sample(self) -> list:
        # return sorted(self._data, key=lambda x: len(x) > 10 and len(x) < 20)
        return self._data[:20]

    def search(self, expression: dict) -> list:
        """Search for specific mails."""

        """
        Description of an expression:
        
        {
            "fields": {
                "field1": "value1",
                "field2": "value2"
                ...
            },
            
            "datetime": {
                "start": "time-str",
                "end": "time-str"
            }
        }
        
        The fields described in "fields" have to match to the fields of the mail
        additionally should the mail be processed between datetime.start and datetime.end
        (including datetime.end)
        
        This is not a generic solution, although still one that provides the user with great flexibility.
        """

        if expression.get('fields') is None:
            # raise
            pass

        if not isinstance(expression['fields'], dict):
            # raise
            pass

        fields = expression['fields']

        # The exception handling with the time conversion should be more fleshed out
        try:
            start = datetime.strptime(expression['datetime']['start'], constants.TIME_FORMAT)
        except Exception as e:
            start = None

        try:
            end = datetime.strptime(expression['datetime']['end'], constants.TIME_FORMAT)
        except Exception as e:
            end = None

        filteredData = []

        for data in self._data:
            mismatch = False

            for key, value in fields.items():
                # TODO: handle this correctly
                if isinstance(data, list):
                    mismatch = True
                    break

                fieldData = data.get(key)
                if fieldData is None or value not in fieldData:
                    mismatch = True
                    break

            if mismatch:
                continue

            if start is not None or end is not None:
                try:
                    mxinTime = datetime.strptime(data.get(constants.PHD_MXIN_TIME), constants.TIME_FORMAT)
                except Exception as e:
                    mxinTime = None

                try:
                    imapTime = datetime.strptime(data.get(constants.PHD_IMAP_TIME), constants.TIME_FORMAT)
                except Exception as e:
                    imapTime = None

                if mxinTime is None and imapTime is None:
                    continue

                def check_time(t1, t2):
                    if t1 is not None and t2 is not None:
                        return t1 >= t2

                    return None

                # get the time where this Mail is first encountered
                dtime = min(x for x in (imapTime, mxinTime) if x is not None)

                startComp = check_time(dtime, start)
                endComp = check_time(end, dtime)

                if startComp is not None and endComp is not None:
                    mismatch = not (startComp & endComp)
                elif startComp is not None:
                    mismatch = not startComp
                elif endComp is not None:
                    mismatch = not endComp


            if mismatch:
                continue

            # if we reached this point there is no missmatch
            # so we add the data to the list of the filtered mails

            filteredData.append(data)

        return filteredData





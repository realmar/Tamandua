"""Module used by the webapp: backend to search the data."""

from datetime import datetime
from ast import literal_eval

from ..serialization.serializer import Serializer
from .. import constants
from .exceptions import ExpressionInvalid

# used in annotation
from ..config import Config


class DataFinder():
    """DataFinder searches given data by fields and/or time."""

    def __init__(self, config: Config) -> None:
        self._config = config
        self._data = []
        self.availableFields = []

        self.load_data()

    def _get_keys(self, inputData: list) -> list:
        """Return a list of all uniq keys."""

        tmpAvailableFields = {}

        for data in inputData:
            for key, value in data.items():
                if tmpAvailableFields.get(key) is None:
                    tmpAvailableFields[key] = True

        return sorted(tmpAvailableFields.keys())

    def load_data(self) -> None:
        """Load data from the data store into memory."""

        self._data = Serializer(self._config).load()['MailContainer']
        self.analise_data()

    def analise_data(self) -> None:
        """
        Analise the data.
        
        Uses _get_keys to get all keys in _data. This method is called from load_data.
        """

        self.availableFields = self._get_keys(self._data)

    def search(self, expression: dict) -> list:
        """Search for specific mails."""

        """
        Description of an expression:
        
        {
            "fields": [
                { "field1": "value1" },
                { "field2": "value2" }
                ...
            ],
            
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

        """
        Validation of fields
        """

        if not isinstance(expression.get('fields'), list):
            fields = []
        else:
            fields = expression['fields']

            counter = 0
            for f in fields:
                currField = 'fields.' + str(counter) + ' '

                if not isinstance(f, dict):
                    raise ExpressionInvalid(currField + 'is not a dict')
                else:
                    if len(f) > 1:
                        raise ExpressionInvalid(currField + 'has more than 1 key value pair')

                counter += 1

        """
        Validation of datetime strings
        """

        datetimeRaw = expression.get('datetime')
        startTimeRaw = None
        endTimeRaw = None

        start = None
        end = None

        if datetimeRaw is not None:
            startTimeRaw = datetimeRaw.get('start')
            endTimeRaw = datetimeRaw.get('end')

            if not isinstance(startTimeRaw, str) or startTimeRaw.strip() == "":
                startTimeRaw = None

            if not isinstance(endTimeRaw, str) or endTimeRaw.strip() == "":
                endTimeRaw = None

        if startTimeRaw is not None:
            try:
                start = datetime.strptime(startTimeRaw, constants.TIME_FORMAT)
            except Exception as e:
                raise ExpressionInvalid("From datetime format is invalid: " + str(startTimeRaw))

        if endTimeRaw is not None:
            try:
                end = datetime.strptime(endTimeRaw, constants.TIME_FORMAT)
            except Exception as e:
                raise ExpressionInvalid("To datetime format is invalid: " + str(endTimeRaw))


        """
        Datafiltering
        """

        filteredData = []

        for data in self._data:
            mismatch = False

            for field in fields:
                for key, value in field.items():
                    try:
                        value = literal_eval(value)
                    except Exception as e:
                        pass

                    if value == '' or value is None:
                        continue

                    fieldData = data.get(key)

                    if fieldData is None:
                        mismatch = True
                        break

                    if isinstance(fieldData, str):
                        if value not in str(fieldData).lower():
                            mismatch = True
                            break
                    else:
                        if value != fieldData:
                            mismatch = True
                            break

                if mismatch:
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

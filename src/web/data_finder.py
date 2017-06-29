"""Module used by the webapp: backend to search the data."""

from datetime import datetime

from .. import constants
from .exceptions import ExpressionInvalid
from ..repository.factory import RepositoryFactory
from ..repository.misc import SearchScope


class DataFinder():
    """DataFinder searches given data by fields and/or time."""

    def __init__(self):
        self._repository = RepositoryFactory.create_repository()
        self.availableFields = self._repository.get_all_keys()


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

        queryData = {}

        for f in fields:
            for k, v in f.items():
                queryData[k] = self._repository.make_regexp(v)

        if start is not None or end is not None:
            queryData[constants.PHD_MXIN_TIME] = self._repository.make_datetime_comparison(start, end)

        results = list(self._repository.find(queryData, SearchScope.ALL))

        for r in results:
            self._repository.remove_metadata(r)

            timeMap = {
                constants.PHD_MXIN_TIME: r.get(constants.PHD_MXIN_TIME),
                constants.PHD_IMAP_TIME: r.get(constants.PHD_IMAP_TIME)
            }

            for key, value in timeMap.items():
                if value is not None:
                    if isinstance(value, list):
                        tmp = []
                        for v in value:
                            tmp.append(datetime.strftime(v, constants.TIME_FORMAT))

                        r[key] = tmp
                    else:
                        r[key] = datetime.strftime(value, constants.TIME_FORMAT)

        return results


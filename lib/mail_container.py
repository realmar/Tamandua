from datetime import datetime
import colorama
colorama.init(autoreset=True)

from .interfaces import IDataContainer, ISerializable
from . import constants
from .plugin_base import RegexFlags

class MailContainer(IDataContainer, ISerializable):
    """Container which aggregates and stores mail objects. This container is optimized for reduced runtime."""

    def __init__(self):
        self._map_qid_mxin = {}
        self._map_qid_imap = {}
        self._map_msgid = {}

    @property
    def subscribedFolder(self) -> str:
        return "mail-aggregation"

    def _merge_data(self, d1: dict, d2: dict) -> None:
        for key, value in d2.items():
            if value is None:
                continue

            d1[key] = value

            """
            # propably needs some sanity checks ...
            if d1.get(key) is None:
                d1[key] = value
            else:
                if d1.key != value:
                    pass   # handle??
            """

    def _aggregate(self, id: str, target: dict, data: dict) -> None:
        if target.get(id) is not None:
            self._merge_data(target[id], data)
        else:
            target[id] = data

    def add_info(self, data: dict) -> None:
        for hasData, flags, d in data['data']:
            if not hasData:
                continue

            mxin_qid = d.get(constants.PHD_MXIN_QID)
            imap_qid = d.get(constants.PHD_IMAP_QID)
            messageid = d.get(constants.MESSAGEID)

            if mxin_qid is not None:
                self._aggregate(mxin_qid, self._map_qid_mxin, d)
            elif imap_qid is not None:
                self._aggregate(imap_qid, self._map_qid_imap, d)
            elif messageid is not None:
                self._aggregate(messageid, self._map_msgid, d)

            if RegexFlags.STORETIME in flags:
                pregexdata = data['pregexdata']
                hostname = pregexdata.get('hostname')

                if hostname is None:
                    continue

                hostname = hostname.replace('-', '')

                if 'mxin' in hostname and mxin_qid is not None:
                    targetData = self._map_qid_mxin
                    targetKey = mxin_qid
                elif 'imap' in hostname and imap_qid is not None:
                    targetData = self._map_qid_imap
                    targetKey = imap_qid
                else:
                    continue

                month = pregexdata.get('month')
                day = pregexdata.get('day')
                time = pregexdata.get('time')

                # prepend '0' to day
                if len(day) == 1:
                    day = '0' + day

                dtStr = '{month} {day} {time}'.format(month=month, day=day, time=time)
                dt = datetime.strptime(dtStr, '%b %d %H:%M:%S')

                # set year to year today (This information is not visible on the logline)
                dt = dt.replace(year=datetime.today().year)

                # bring datetime in a portable format
                newDtStr = dt.strftime('%Y/%m/%d %H:%M:%S')
                try:
                    targetData[targetKey][
                        constants.HOSTNAME_TIME_MAP[
                            hostname
                        ]] = newDtStr
                except Exception as e:
                    # TODO: handle
                    pass

    def represent(self) -> None:
        for qid, d in self._map_qid_mxin.items():
            print('\n==== MAIL: ====\n')

            def print_title(key, value):
                print('---- ' + key + ': ' +
                      colorama.Style.BRIGHT +
                      str(value) +
                      colorama.Style.NORMAL +
                      ' ----')

            def print_content(data):
                for key, value in data.items():
                    print(colorama.Style.BRIGHT + key + colorama.Style.NORMAL + ': ' + str(value))


            print_title('Queue-ID phd-mxin', qid)
            print_content(d)

            if d.get(constants.PHD_IMAP_QID) is not None:
                data = self._map_qid_imap.get(d.get(constants.PHD_IMAP_QID))

                if data is not None and len(data) > 0:
                    print('\n')
                    print_title('Queue-ID phd-imap', d.get(constants.PHD_IMAP_QID))
                    print_content(data)

            if d.get(constants.MESSAGEID) is not None and len(d.get(constants.MESSAGEID)) > 0:
                data = self._map_msgid.get(d.get(constants.MESSAGEID))

                if data is not None and len(data) > 0:
                    print('\n')
                    print_title('Message-ID', d.get(constants.MESSAGEID))
                    print_content(data)

    def get_serializable_data(self) -> object:
        return {
            constants.PHD_MXIN_QID: self._map_qid_mxin,
            constants.PHD_IMAP_QID: self._map_qid_imap,
            constants.MESSAGEID: self._map_msgid
        }
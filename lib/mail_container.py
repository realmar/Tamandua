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

    def _merge_data(self, target: dict, origin: dict) -> None:
        for key, value in origin.items():
            if value is None:
                continue

            if target.get(key) is None:
                target[key] = value
            else:
                if target[key] != value:
                    if not isinstance(target[key], list):
                        target[key] = [target[key], value]
                    else:
                        target[key].append(value)
                else:
                    continue

    def _aggregate(self, id: str, target: dict, data: dict, logline: str) -> None:
        if id == constants.NOQUEUE:
            data[constants.LOGLINES] = logline

            if not isinstance(target.get(id), list):
                target[id] = [data]
            else:
                target[id].append(data)

            return

        # else: if the queue is not NOQUEUE

        if target.get(id) is not None:
            self._merge_data(target[id], data)
        else:
            target[id] = data

        if not isinstance(target[id].get(constants.LOGLINES), list):
            target[id][constants.LOGLINES] = [ logline ]
        else:
            target[id][constants.LOGLINES].append(logline)

    def add_info(self, data: dict) -> None:
        logline = data['raw_logline']

        for hasData, flags, d in data['data']:
            if not hasData:
                continue

            mxin_qid = d.get(constants.PHD_MXIN_QID)
            imap_qid = d.get(constants.PHD_IMAP_QID)
            messageid = d.get(constants.MESSAGEID)

            if mxin_qid is not None:
                self._aggregate(mxin_qid, self._map_qid_mxin, d, logline)
            elif imap_qid is not None:
                self._aggregate(imap_qid, self._map_qid_imap, d, logline)
            elif messageid is not None:
                self._aggregate(messageid, self._map_msgid, d, logline)

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
                def inner_print(d):
                    for key, value in d.items():
                        if key is not constants.LOGLINES:
                            print(colorama.Style.BRIGHT + key + colorama.Style.NORMAL + ': ' + str(value))

                    if isinstance(d.get(constants.LOGLINES), list):
                        print('\n-- ' +
                              colorama.Style.BRIGHT +
                              'corresponding loglines:' +
                              colorama.Style.NORMAL +
                              ' --')

                        for line in d.get(constants.LOGLINES):
                            print(colorama.Fore.LIGHTBLACK_EX + line.strip())

                if isinstance(data, list):
                    for entry in data:
                        inner_print(entry)
                        print('\n')
                else:
                    inner_print(data)


            print_title('Queue-ID phd-mxin', qid)
            print_content(d)

            def inner_represent(d):
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

            if isinstance(d, list):
                for entry in d:
                    inner_represent(entry)
            else:
                inner_represent(d)



    def get_serializable_data(self) -> object:
        return {
            constants.PHD_MXIN_QID: self._map_qid_mxin,
            constants.PHD_IMAP_QID: self._map_qid_imap,
            constants.MESSAGEID: self._map_msgid
        }
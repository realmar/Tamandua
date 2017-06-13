"""Module which contains the DataContainer class."""

from datetime import datetime
from typing import List, Dict
import copy
import colorama
colorama.init(autoreset=True)

from ..interfaces import IDataContainer, ISerializable, IRequiresPlugins
from .. import constants
from ..plugins.plugin_base import RegexFlags
from ..plugins.plugin_processor import ProcessorData, ProcessorAction


class MailContainer(IDataContainer, ISerializable, IRequiresPlugins):
    """Container which aggregates and stores mail objects."""

    def __init__(self):
        self._map_qid_mxin = {}
        self._map_qid_imap = {}
        self._map_msgid = {}
        # this will store all mailfragments which where "sent" by the pickup service
        # map : imap_qid -> mail-fragment
        self._map_pickup = {}

        self._final_data = []

        self._pluginManager = None

    @property
    def subscribedFolder(self) -> str:
        """Return the folder name from which we want the plugin data."""
        return "mail-aggregation"

    def set_pluginmanager(self, pluginManager: 'PluginManager') -> None:
        self._pluginManager = pluginManager

    def _merge_data(self, target: dict, origin: dict) -> None:
        """Generic merge method."""
        for key, value in origin.items():
            if value is None:
                continue

            if target.get(key) is None:
                target[key] = value
            else:
                if target[key] != value:
                    if not isinstance(target[key], list):
                        if isinstance(value, list):
                            # make items unique
                            value = list(set(value))

                            if target[key] not in value:
                                # WARNING: incompatible with python 3.4:
                                # SyntaxError: can use starred expression only as assignment target
                                #
                                #                            unpack values in value
                                #                               v
                                # target[key] = [target[key], *value]

                                # following is compatible for python 3.4 and onwards
                                tmp = [target[key]]
                                tmp.extend(value)

                                target[key] = tmp
                        else:
                            target[key] = [target[key], value]
                    else:
                        if isinstance(value, list):
                            # make items uniq
                            value = list(set(value))

                            uniqList = []

                            # filter uniq items
                            for v in value:
                                if v not in target[key]:
                                    uniqList.append(v)

                            # only append uniq items
                            target[key].extend(uniqList)
                        else:
                            if value not in target[key]:
                                target[key].append(value)
                else:
                    continue

    def _aggregate_fragment(self, id: str, target: dict, data: dict, logline: str) -> None:
        """Aggregate data."""
        if id == constants.NOQUEUE:
            data[constants.LOGLINES] = [logline]

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

    def add_fragment(self, data: dict) -> None:
        """Add data to the container."""

        logline = data['raw_logline']

        for hasData, flags, d in data['data']:
            if not hasData:
                continue

            mxin_qid = d.get(constants.PHD_MXIN_QID)
            imap_qid = d.get(constants.PHD_IMAP_QID)
            messageid = d.get(constants.MESSAGEID)

            pregexdata = data['pregexdata']
            hostname = pregexdata.get('hostname')

            # if the STORETIME flag is present, we store the date and time
            # which is given by the logline
            if RegexFlags.STORETIME in flags and ('mxin' in hostname or 'imap' in hostname) and hostname is not None:
                hostname = hostname.replace('-', '')

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
                newDtStr = dt.strftime(constants.TIME_FORMAT)
                try:
                    d[constants.HOSTNAME_TIME_MAP[hostname]] = newDtStr
                except Exception as e:
                    pass

            if mxin_qid is not None:
                self._aggregate_fragment(mxin_qid, self._map_qid_mxin, d, logline)
            elif imap_qid is not None:
                if RegexFlags.PICKUP in flags or self._map_pickup.get(imap_qid) is not None:
                    self._aggregate_fragment(imap_qid, self._map_pickup, d, logline)

                    prev_map = self._map_qid_imap.get(imap_qid)
                    if prev_map is not None:
                        self._merge_data(self._map_pickup, prev_map)
                        del self._map_qid_imap[imap_qid]

                else:
                    self._aggregate_fragment(imap_qid, self._map_qid_imap, d, logline)
            elif messageid is not None:
                self._aggregate_fragment(messageid, self._map_msgid, d, logline)

    def __merge_pickup(self, mail: dict, msgid: str) -> None:
        if msgid is None:
            return

        for qid, m in self._map_pickup.items():
            for k, v in m.items():
                if k == constants.MESSAGEID and msgid == v:
                    self._merge_data(mail, m)
                    del self._map_pickup[qid]
                    return

    def __postprocessing(self, mail: dict) -> ProcessorAction:
        if self._pluginManager is not None:
            chain = self._pluginManager.get_chain_with_responsibility('postprocessors')
            if chain is not None:
                pd = ProcessorData(mail)
                chain.process(pd)
                return pd.action

    def __aggregate_mails(self,
                          fragments: dict,
                          fragmentChain: List[Dict[str, dict]],
                          keyChain: List[str]) -> None:
        """
        Abstract:
        TODO
        This method does the actual aggregation of multiple fragments into multiple mail-objects.

        Description:
        TODO

        """

        def __agg_wrapp(frag: dict) -> dict:
            # create aggregate target
            target = copy.deepcopy(frag)

            for index in range(len(keyChain)):
                nextid = target.get(keyChain[index])
                toDelete = []
                if nextid is not None:
                    def agg_nextid(id):
                        otherFrag = fragmentChain[index].get(id)
                        if otherFrag is not None:
                            self._merge_data(target, otherFrag)
                            # cannot delete object now, as it would break the iteration
                            toDelete.append(
                                (index, id)
                            )

                    if isinstance(nextid, list):
                        for n in nextid:
                            agg_nextid(n)
                    else:
                        agg_nextid(nextid)

                    for id1, id2 in toDelete:
                        del fragmentChain[id1][id2]
                else:
                    continue

            return target

        def __post(target: dict):
            self.__merge_pickup(target, target.get(constants.MESSAGEID))
            if self.__postprocessing(target) != ProcessorAction.DELETE:
                self._final_data.append(target)

        for id, frag in fragments.items():
            if isinstance(frag, list):
                for f in frag:
                    __post(__agg_wrapp(f))

            else:
                __post(__agg_wrapp(frag))

        fragments.clear()

    def build_final(self) -> None:
        """Aggregate data to mail objects."""
        self.__aggregate_mails(
            self._map_qid_mxin,
            [
                self._map_qid_imap,
                self._map_msgid
            ],
            [
                constants.PHD_IMAP_QID,
                constants.MESSAGEID,
            ]
        )

        self.__aggregate_mails(
            self._map_qid_imap,
            [
                self._map_msgid
            ],
            [
                constants.MESSAGEID
            ]
        )

        self.__aggregate_mails(
            self._map_msgid,
            [],
            []
        )

        for m in self._map_pickup.values():
            if self.__postprocessing(m) != ProcessorAction.DELETE:
                self._final_data.append(m)

        self._map_pickup.clear()

    def represent(self) -> None:
        """Print the contents of this container in a human readable format to stdout."""

        def print_title(**kv):
            finalStr = '---- '
            for k, v in kv.items():
                finalStr += k + ': ' + colorama.Style.BRIGHT + str(v) + colorama.Style.NORMAL + ' '

            finalStr += '----'

            print(finalStr)

        def print_list(key, value):
            print('    ' + colorama.Style.BRIGHT + key)
            for v in value:
                print('        ' + str(v).strip())

        print('\n========' + colorama.Style.BRIGHT + ' List of collected Mails ' +
              colorama.Style.NORMAL + '========')

        # begin printing mails

        for mail in self._final_data:
            print('\n')
            print(colorama.Back.LIGHTMAGENTA_EX + '>>>>' * 4 + colorama.Style.BRIGHT + ' Mail ' +
                  colorama.Style.NORMAL + '<<<<' * 4)

            mxin_qid = mail.get(constants.PHD_MXIN_QID)
            imap_qid = mail.get(constants.PHD_IMAP_QID)
            msgid = mail.get(constants.MESSAGEID)

            d = {}

            if imap_qid is not None:
                d['Queue-ID phd-imap'] = imap_qid

            if mxin_qid is not None:
                d['Queue-ID phd-mxin'] = mxin_qid

            if msgid is not None:
                d['Message-ID'] = msgid

            print_title(**d)

            for key, value in sorted(mail.items(), key=lambda x: x[0]):
                if key == constants.LOGLINES:
                    continue

                if isinstance(value, list):
                    print_list(key, value)
                else:
                    print('    ' + colorama.Style.BRIGHT + key + colorama.Style.NORMAL + ': ' + str(value))

            loglines = mail.get(constants.LOGLINES)
            if loglines is not None:
                print_list(constants.LOGLINES, loglines)

    def get_serializable_data(self) -> object:
        """Return data which should and can be serialized."""
        return self._final_data

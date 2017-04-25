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

        """
        self._data = []
        self._incomplete_data = []

        # caches for runtime optimization

        self._qidMxinCache = {}
        self._qidImapCache = {}
        self._msgidCache = {}

        self._incompleteQidImapCache = {}
        self._incompleteMsgidCache = {}
        """

    @property
    def subscribedFolder(self) -> str:
        return "mail-aggregation"

    def _merge_data(self, d1: dict, d2: dict) -> None:
        pass

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

                dtStr = '{month} {day} {time}'.format(month, day, time)
                dt = datetime.strptime(dtStr, '%b %d %H:%M:%S')

                # set year to year today (This information is not visible on the logline)
                dt = dt.replace(year=datetime.today().year)

                # bring datetime in a portable format
                newDtStr = dt.strftime('%Y/%m/%d %H:%M:%S')
                try:
                    targetData[targetKey][
                        constants.TIME_HOSTNAME_MAP[
                            hostname
                        ]] = newDtStr
                except Exception as e:
                    # TODO: handle
                    pass





    """
    def _merge_data(self, d1: dict, d2: dict) -> dict:
        pass

    def _aggregate(self, cache, data, key):
        cache[key] = self._merge_data(
            cache[key],
            data
        )

    def add_info(self, data: dict) -> None:
        pregexdata = data['pregexdata']

        for hasData, d in data['data']:
            if not hasData:
                continue

            mxin_qid = d.get(constants.PHD_MXIN_QID)
            imap_qid = d.get(constants.PHD_IMAP_QID)
            messageid = d.get(constants.MESSAGEID)

            # TODO: retroactively add qid imap and msgid to caches
            # TODO: store logline with data


            def update_caches():
                if imap_qid is not None:
                    if self._incompleteQidImapCache.get(imap_qid) is not None:
                        self._aggregate(self._qidMxinCache, self._incompleteQidImapCache[imap_qid], mxin_qid)

                        # WARNING: Currently the data will not be deleted from the incomplete-caches --> too costly
                        # self._incomplete_data.remove(self._incompleteQidImapCache[imap_qid])
                        del self._incompleteQidImapCache[imap_qid]

                    self._qidImapCache[imap_qid] = self._qidMxinCache[mxin_qid]

                if messageid is not None:
                    if self._msgidCache.get(messageid) is not None:
                        self._aggregate(self._qidMxinCache, self._msgidCache[messageid], mxin_qid)

                        # do not delete the stored Mail in the msgid cache
                        # as it may be needed for other Mails

                    if not isinstance(self._msgidCache[messageid], list):
                        self._msgidCache[messageid] = [self._qidMxinCache[mxin_qid]]
                    else:
                        alreadyContainsMail = False
                        for mail in self._msgidCache[messageid]:
                            if mail is self._qidMxinCache[mxin_qid]:
                                alreadyContainsMail = True

                        if not alreadyContainsMail:
                            self._msgidCache[messageid].append(self._qidMxinCache[mxin_qid])

            if mxin_qid is not None:
                if self._qidMxinCache.get(mxin_qid) is not None:
                    self._aggregate(self._qidMxinCache, d, mxin_qid)
                else:
                    self._data.append(d)
                    self._qidMxinCache[mxin_qid] = d

                update_caches()

            elif imap_qid is not None:
                if self._qidImapCache.get(imap_qid) is not None:
                    self._aggregate(self._qidImapCache, d, imap_qid)
                else:
                    if self._incompleteQidImapCache.get(imap_qid) is not None:
                        self._aggregate(self._incompleteQidImapCache)
                    else:
                        self._incomplete_data.append(d)
                        self._incompleteQidImapCache[imap_qid] = d

            elif messageid is not None:
                if self._msgidCache is not None:
                    self._aggregate(self._msgidCache, d, messageid)
                else:
                    if self._incompleteMsgidCache.get(messageid) is not None:
                        self._aggregate(self._incompleteMsgidCache, d, messageid)
                    else:
                        self._incomplete_data.append(d)
                        self._incompleteMsgidCache[messageid] = d
            else:
                # Not good. This should never happen ... handle this!
                pass
    """


    def represent(self) -> None:
        for d in self._map_qid_mxin:
            print('===============')
            print('==== MAIL: ====')
            print('===============\n')

            def print_title(key, value):
                print('---- ' + key + ': ' +
                      colorama.Style.BRIGHT +
                      value +
                      colorama.Style.NORMAL +
                      ' ----')

            def print_content(data):
                if data is None:
                    return

                for key, value in data:
                    print(colorama.Style.BRIGHT + key + colorama.Style.NORMAL + ': ' + value)


            print_title('Queue-ID phd-mxin', d.get(constants.PHD_MXIN_QID))
            print_content(d)

            if d.get(constants.PHD_IMAP_QID) is not None:
                print_title('Queue-ID phd-imap', d.get(constants.PHD_IMAP_QID))
                print_content(self._map_qid_imap.get(d.get(constants.PHD_IMAP_QID)))

            if d.get(constants.MESSAGEID) is not None:
                print_title('Message-ID', d.get(constants.MESSAGEID))
                print_content(self._map_msgid.get(d.get(constants.MESSAGEID)))

    def get_serializable_data(self) -> object:
        return {
            constants.PHD_MXIN_QID: self._map_qid_mxin,
            constants.PHD_IMAP_QID: self._map_qid_imap,
            constants.MESSAGEID: self._map_msgid
        }
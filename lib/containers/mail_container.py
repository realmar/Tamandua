"""Module which contains the DataContainer class."""

from datetime import datetime
import typing
# import copy
import colorama
colorama.init(autoreset=True)

from ..interfaces import IDataContainer, ISerializable, IRequiresPlugins
from .. import constants
from ..plugins.plugin_base import RegexFlags


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

        self._integrity_stats = {}

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

    def _aggregate(self, id: str, target: dict, data: dict, logline: str) -> None:
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

    def add_info(self, data: dict) -> None:
        """Add data to the container."""

        # if we add new data but have already generated some integrity stats
        # then we need to erase them, as those stats become out dated
        if len(self._integrity_stats) > 0:
            self._integrity_stats = {}

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
                self._aggregate(mxin_qid, self._map_qid_mxin, d, logline)
            elif imap_qid is not None:
                if RegexFlags.PICKUP in flags or self._map_pickup.get(imap_qid) is not None:
                    self._aggregate(imap_qid, self._map_pickup, d, logline)

                    prev_map = self._map_qid_imap.get(imap_qid)
                    if prev_map is not None:
                        self._merge_data(self._map_pickup, prev_map)
                        del self._map_qid_imap[imap_qid]

                else:
                    self._aggregate(imap_qid, self._map_qid_imap, d, logline)
            elif messageid is not None:
                self._aggregate(messageid, self._map_msgid, d, logline)

    def build_final(self) -> None:
        """Aggregate data to mail objects and generate integrity stats."""

        """
        
        integrity stats description:
        
        total_mails
            total count of mails, complete or incomplete
        
        total_mxin
            total mails with a queueid from phd-mxin
        
        total_no_mxin
            Count of mails where the queueid of phd-mxin is unknown
            
            meaning that the queueid of phd-imap is known but the queueid of
            phd-mxin is unkonwn and the messageid may be known
        
        only_mxin_qid
            Count of mails where only the queueid of phd-mxin is known
            
        only_imap_qid
            Count of mails where only the queueid of phd-imap is known
        
        only_messageid
            Count of mails where only the messageid is known
        
        missing_fields
            Counts fields which are missing from incomplete Mails
        """
        self._integrity_stats = {
            'total_mails': 0,
            'total_mxin': 0,
            # 'total_no_mxin': 0,

            # 'only_mxin_qid': 0,
            # 'only_imap_qid': 0,
            # 'only_messageid': 0,

            'complete_mails': 0,
            'incomplete_mails': 0,

            # 'missing_fields': {}
        }

        self._final_data = []
        self._final_incomplete_data = []

        known_qids_imap = {}
        known_msgids = {}

        #
        # verify_fields contains rules which determines if a mail if complete or not
        #

        def verify_fields(mail):
            def check_fields(requiredFields) -> bool:
                # isComplete = True

                for field in requiredFields:
                    if mail.get(field) is None:
                        """
                        isComplete = False

                        d = self._integrity_stats['missing_fields']
                        if not isinstance(d.get(field), int):
                            d[field] = 1
                        else:
                            d[field] += 1
                        """

                        return False

                # return isComplete
                return True

            def check_fieldcontent(field: typing.Union[str, list], other: str):
                if field is None:
                    return False

                if isinstance(field, str):
                    return other in field.lower()
                elif isinstance(field, list):
                    for f in field:
                        if other in f.lower():
                            return True

                    return False
                else:
                    pass
                    # TODO: handle

            action = mail.get('action')
            if check_fieldcontent(action, 'hold') or check_fieldcontent(action, 'reject'):
                mail[constants.COMPLETE] = True
                mail[constants.DESTINATION] = constants.DESTINATION_HOLD

            virusresult = mail.get('virusresult')
            if check_fieldcontent(virusresult, 'passed'):
                mail[constants.DESTINATION] = constants.DESTINATION_VIRUS

                if not check_fields([
                    'sender',
                    'recipient',
                    'virusresult',
                    'virusaction'
                ]):
                    mail[constants.COMPLETE] = False
                else:
                    mail[constants.COMPLETE] = True

            deliverystatus = mail.get('deliverystatus')
            if check_fieldcontent(deliverystatus, 'sent'):
                mail[constants.COMPLETE] = True
                mail[constants.DESTINATION] = constants.DESTINATION_DELIVERED

                if not check_fields([
                    'sender',
                    'recipient',
                    'virusresult',
                    'virusaction',
                    'deliverystatus',
                    'deliverymessage',
                    'deliveryrelay',
                    'spamscore',
                    'spamrequiredscore',
                    'spamdesc',
                    constants.USERNAME,
                    constants.UID,
                    'size'
                ]):
                    mail[constants.COMPLETE] = False
                else:
                    mail[constants.COMPLETE] = True

            if mail.get(constants.COMPLETE) is None:
                mail[constants.COMPLETE] = False
                mail[constants.DESTINATION] = constants.DESTINATION_UNKOWN

        def merge_pickup(finalMail: dict, msgid: str):
            if msgid is None:
                return

            for qid_imap, mail in self._map_pickup.items():
                for k, v in mail.items():
                    if k == constants.MESSAGEID and msgid == v:
                        self._merge_data(finalMail, mail)
                        del self._map_pickup[qid_imap]
                        return

        def do_postprocessing(finalMail: dict) -> None:
            if self._pluginManager is not None:
                chain = self._pluginManager.get_chain_with_responsibility('postprocessors')
                chain.process(finalMail)

        #
        # collect complete data
        #

        for qid, mail in self._map_qid_mxin.items():
            if isinstance(mail, list):
                # rejected mails, which have the same qid (NOQUEUE)
                for m in mail:
                    m[constants.COMPLETE] = True
                    m[constants.DESTINATION] = constants.DESTINATION_REJECT

                    self._integrity_stats['complete_mails'] += 1
                    # self._integrity_stats['only_mxin_qid'] += 1

                    self._final_data.append(m)

                continue

            # finalMail = copy.deepcopy(mail)
            finalMail = mail

            msgid = mail.get(constants.MESSAGEID)
            qid_imap = mail.get(constants.PHD_IMAP_QID)

            # it may be possible to have multiple queueids which map to the same mail on phd-mxin
            # this is when a user sends a mail to multiple persons at the same time.
            #
            # we solve that by always assuming multiple queueids on phd-imap which map to one
            # queueid on phd-mxin --> if there is only one qid then we will just put it into
            # a list (where this qid is the only item)

            if not isinstance(qid_imap, list):
                qids_imap = [qid_imap]
            else:
                qids_imap = qid_imap

            for qid_imap in qids_imap:
                data_imap = self._map_qid_imap.get(qid_imap)

                # collect data for corresponding queueid on phd-imap

                if qid_imap is not None:
                    known_qids_imap[qid_imap] = True

                if data_imap is not None:
                    if msgid is None:
                        msgid = data_imap.get(constants.MESSAGEID)

                    self._merge_data(finalMail, data_imap)
                """
                else: 
                    if msgid is None:
                        self._integrity_stats['only_mxin_qid'] += 1
                """

                # collect data for corresponding messageid

                if msgid is not None:
                    if isinstance(msgid, list):
                        msgids = msgid
                    else:
                        msgids = [msgid]

                    for msgid in msgids:
                        known_msgids[msgid] = True

                        data_msgid = self._map_msgid.get(msgid)

                        if data_msgid is not None:
                            self._merge_data(finalMail, data_msgid)

            # determine destination and verify integrity

            verify_fields(finalMail)

            if not finalMail[constants.COMPLETE]:
                self._integrity_stats['incomplete_mails'] += 1
            else:
                self._integrity_stats['complete_mails'] += 1

            merge_pickup(finalMail, msgid)
            do_postprocessing(finalMail)

            self._final_data.append(finalMail)

        #
        # collect incomplete data --> mails which do not have a queueid on phd-mxin
        #

        #
        # get imap unknown
        #

        for qid, mail in self._map_qid_imap.items():
            if known_qids_imap.get(qid) is not None:
                continue

            if isinstance(mail, list):
                # rejected mails on phd-imap (mailman)
                for m in mail:
                    m[constants.COMPLETE] = True
                    m[constants.DESTINATION] = constants.DESTINATION_REJECT

                    self._integrity_stats['complete_mails'] += 1
                    # self._integrity_stats['total_no_mxin'] += 1
                    # self._integrity_stats['only_imap_qid'] += 1

                    self._final_data.append(m)

                continue

            self._integrity_stats['incomplete_mails'] += 1
            # self._integrity_stats['total_no_mxin'] += 1
            msgid_imap = mail.get(constants.MESSAGEID)

            # incompleteMail = copy.deepcopy(mail)
            incompleteMail = mail
            verify_fields(incompleteMail)
            incompleteMail[constants.COMPLETE] = False


            if msgid_imap is not None:
                known_msgids[msgid_imap] = True
                msgid_mail = self._map_msgid.get(msgid_imap)

                if msgid_mail is not None:
                    self._merge_data(incompleteMail, msgid_mail)
            """
            else:
                self._integrity_stats['only_imap_qid'] += 1
            """

            merge_pickup(incompleteMail, msgid_imap)
            do_postprocessing(finalMail)

            self._final_data.append(incompleteMail)

        #
        # get messageid unknown
        #

        for msgid, mail in self._map_msgid.items():
            if known_msgids.get(msgid) is not None:
                continue

            self._integrity_stats['incomplete_mails'] += 1
            # self._integrity_stats['only_messageid'] += 1

            # incompleteMail = copy.deepcopy(mail)
            incompleteMail = mail
            verify_fields(incompleteMail)
            incompleteMail[constants.COMPLETE] = False

            merge_pickup(incompleteMail, msgid)
            do_postprocessing(finalMail)

            self._final_data.append(incompleteMail)

        #
        # only pickup mails
        #

        self._final_data.extend(self._map_pickup.values())

        # global stats

        self._integrity_stats['total_mails'] = len(self._final_data)
        self._integrity_stats['total_mxin'] = len(self._map_qid_mxin)

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

    def print_integrity_report(self) -> None:
        """Print the integrity report to stdout."""
        print('\n========' + colorama.Style.BRIGHT + ' Integrity Report ' + colorama.Style.NORMAL + '========')

        if len(self._integrity_stats) == 0:
            print(
                'No integrity stats for ' + colorama.Style.BRIGHT + self.__class__.__name__
                + colorama.Style.NORMAL + ' at the moment.\n'
                'Please run ' + self.__class__.__name__ + '.build_final() to generate integrity data.'
            )
        else:
            def p(indent: int, key: str, value: str) -> None:
                print(' ' * indent + colorama.Style.BRIGHT + key + ': ' + colorama.Style.NORMAL + str(value))

            for key, value in sorted(self._integrity_stats.items(), key=lambda x: x[0]):
                if isinstance(value, dict):
                    for k, v in value.items():
                        p(4, k, v)
                else:
                    p(0, key, value)

    def get_serializable_data(self) -> object:
        """Return data which should and can be serialized."""
        return self._final_data

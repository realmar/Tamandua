from datetime import datetime
import copy
import colorama
colorama.init(autoreset=True)

from ..interfaces import IDataContainer, ISerializable
from .. import constants
from ..plugins.plugin_base import RegexFlags

class MailContainer(IDataContainer, ISerializable):
    """Container which aggregates and stores mail objects. This container is optimized for reduced runtime."""

    def __init__(self):
        self._map_qid_mxin = {}
        self._map_qid_imap = {}
        self._map_msgid = {}

        self._final_data = []

        self._integrity_stats = {}

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
                        if isinstance(value, list):
                            #                            unpack values in value
                            #                               v
                            target[key] = [target[key], *value]
                        else:
                            target[key] = [target[key], value]
                    else:
                        if isinstance(value, list):
                            target[key].extend(value)
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
        # if we add new data but have already generate some integrity stats
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
            
        """
        self._integrity_stats = {
            'total_mails': 0,
            'total_mxin': 0,
            'total_no_mxin': 0,

            'only_mxin_qid': 0,
            'only_imap_qid': 0,
            'only_messageid': 0,

            'complete_mails': 0,
            'incomplete_mails': 0
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
                for field in requiredFields:
                    if mail.get(field) is None:
                        return False

                return True

            action = mail.get('action')
            if action is not None and action == 'hold':
                mail[constants.COMPLETE] = True
                mail[constants.DESTINATION] = constants.DESTINATION_HOLD

            virusresult = mail.get('virusresult')
            if virusresult is not None and 'passed' not in virusresult.lower():
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
            if deliverystatus is not None and 'sent' in deliverystatus.lower():
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
                    'spamuser'
                    'spamuid',
                    'size'
                ]):
                    mail[constants.COMPLETE] = False
                else:
                    mail[constants.COMPLETE] = True

            if mail.get(constants.COMPLETE) is None:
                mail[constants.COMPLETE] = False
                mail[constants.DESTINATION] = constants.DESTINATION_UNKOWN

        #
        # collect complete data
        #

        for qid, mail in self._map_qid_mxin.items():
            if isinstance(mail, list):
                # rejected mails, which have the same qid (NOQUEUE)
                mail[constants.COMPLETE] = True
                mail[constants.DESTINATION] = constants.DESTINATION_REJECT

                self._final_data.append(mail)
            else:
                finalMail = copy.deepcopy(mail)

                msgid = mail.get(constants.MESSAGEID)
                qid_imap = mail.get(constants.PHD_IMAP_QID)

                data_imap = self._map_qid_imap.get(qid_imap)

                # collect data for corresponding queueid on phd-imap

                if data_imap is not None:
                    known_qids_imap[qid_imap] = None

                    if msgid is None:
                        msgid = data_imap.get(constants.MESSAGEID)

                    self._merge_data(finalMail, data_imap)
                else:
                    if msgid is None:
                        self._integrity_stats['only_mxin_qid'] += 1

                # collect data for corresponding messageid

                if msgid is not None:
                    known_msgids[msgid] = None

                    data_msgid = self._map_msgid.get(msgid)

                    if data_msgid is not None:
                        self._merge_data(finalMail, data_msgid)

                # determine destination and verify integrity

                verify_fields(finalMail)

                if not finalMail[constants.COMPLETE]:
                    self._integrity_stats['incomplete_mails'] += 1
                else:
                    self._integrity_stats['complete_mails'] += 1

                self._final_data.append(finalMail)

        #
        # collect incomplete data --> mails which do not have a queueid on phd-mxin
        #

        known_msgids_imap = {}

        # get imap unknown

        for qid, mail in self._map_qid_imap.items():
            if known_qids_imap.get(qid) is None:
                self._integrity_stats['incomplete_mails'] += 1
                self._integrity_stats['total_no_mxin'] += 1
                msgid_imap = mail.get(constants.MESSAGEID)

                incompleteMail = copy.deepcopy(mail)
                verify_fields(incompleteMail)
                incompleteMail[constants.COMPLETE] = False


                if msgid_imap is not None:
                    known_msgids_imap[msgid_imap] = None
                    msgid_mail = self._map_msgid.get(msgid_imap)

                    if msgid_mail is not None:
                        self._merge_data(incompleteMail, msgid_mail)
                else:
                    self._integrity_stats['only_imap_qid'] += 1

                self._final_data.append(incompleteMail)

        # get messageid unknown

        for msgid, mail in self._map_msgid.items():
            if known_msgids_imap.get(msgid) is None:
                self._integrity_stats['incomplete_mails'] += 1
                self._integrity_stats['only_messageid'] += 1

                incompleteMail = copy.deepcopy(mail)
                verify_fields(incompleteMail)
                incompleteMail[constants.COMPLETE] = False

                self._final_data.append(incompleteMail)

        # global stats

        self._integrity_stats['total_mails'] = len(self._final_data)
        self._integrity_stats['total_mxin'] = len(self._map_qid_mxin)

    def represent(self) -> None:
        def print_title(**kv):
            finalStr = '---- '
            for k, v in kv.items():
                finalStr += k + ': ' + colorama.Style.BRIGHT + str(v) + colorama.Style.NORMAL + ' '

            finalStr += '----'

            print(finalStr)

        def inner_print_content(data):
            def print_list(key, value):
                print('    ' + colorama.Style.BRIGHT + key)
                for v in value:
                    print('        ' + v.strip())

            for key, value in sorted(data.items(), key=lambda x: x[0]):
                if key == constants.LOGLINES:
                    continue

                if isinstance(value, list):
                    print_list(key, value)
                else:
                    print('    ' + colorama.Style.BRIGHT + key + colorama.Style.NORMAL + ': ' + str(value))

            loglines = data.get(constants.LOGLINES)
            if loglines is not None:
                print_list(constants.LOGLINES, loglines)

        print('\n========' + colorama.Style.BRIGHT + ' List of collected Mails ' +
              colorama.Style.NORMAL + '========')

        # begin printing mails

        for mail in self._final_data:
            print('\n')
            print(colorama.Back.LIGHTMAGENTA_EX + '>>>>' * 4 + colorama.Style.BRIGHT + ' Mail ' +
                  colorama.Style.NORMAL + '<<<<' * 4)

            if isinstance(mail, list):
                # now we have a list of mails without a queueid, or rather NOQUEUE

                print_title(**{'No Queue-ID': 'NOQUEUE'})
                for m in mail:
                    inner_print_content(m)
            else:
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
                inner_print_content(mail)

    def print_integrity_report(self) -> None:
        print('\n========' + colorama.Style.BRIGHT + ' Integrity Report ' + colorama.Style.NORMAL + '========')

        if len(self._integrity_stats) == 0:
            print(
                'No integrity stats for ' + colorama.Style.BRIGHT + self.__class__.__name__
                + colorama.Style.NORMAL + ' at the moment.\n'
                'Please run ' + self.__class__.__name__ + '.build_final() to generate integrity data.'
            )
        else:
            for key, value in sorted(self._integrity_stats.items(), key=lambda x: x[0]):
                print(colorama.Style.BRIGHT + key + ': ' + colorama.Style.NORMAL + str(value))

    def get_serializable_data(self) -> object:
        """Return data which should and can be serialized."""
        return self._final_data

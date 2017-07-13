"""Module which contains the MailContainer class."""

import copy
import sys
from datetime import datetime
from typing import List, Dict
from functools import partial
from pprint import pprint

from src.plugins.interfaces import IDataContainer, IRequiresPlugins, IRequiresRepository
from src.repository.interfaces import IRepository
from src import constants
from src.plugins.bases.plugin_base import RegexFlags
from src.plugins.bases.plugin_processor import ProcessorData, ProcessorAction
from src.repository.misc import SearchScope
from src.plugins.bases.mail_edge_case_processor import MailEdgeCaseProcessorData
from src.expression.builder import ExpressionBuilder, ExpressionField, Comparator
from src.config import Config


class AlreadyInRepository(Exception):
    pass


class MailContainer(IDataContainer, IRequiresPlugins, IRequiresRepository):
    """
    Container which aggregates and stores mail objects.

    Nomenclature:
    fragment:   a fragment is a part of a mail-object, this fragment is then merged with
                other fragments into one mail-object. Eg. such a fragment could be all
                data of a mail from phd-mxin.
    """


    def __init__(self):
        self._map_qid_mxin = {}
        self._map_qid_imap = {}
        self._map_msgid = {}
        # this will store all mailfragments which where "sent" by the pickup service
        # map : imap_qid -> mail-fragment
        self._map_pickup = {}

        self._pluginManager = None
        self._repository = None

        # metadata
        self.__build_final_metadata = {}

    @property
    def subscribedFolder(self) -> str:
        """Return the folder name from which we want the plugin data."""
        return "mail-aggregation"

    def set_pluginmanager(self, pluginManager: 'PluginManager') -> None:
        self._pluginManager = pluginManager

    def set_repository(self, repository: IRepository) -> None:
        self._repository = repository

    @staticmethod
    def _merge_data(target: dict, origin: dict) -> None:
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
                                # SyntaxError: can use starred expression
                                #              only as assignment target
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
            target[id][constants.LOGLINES] = [logline]
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
                # we can handle this datetime objects now
                # newDtStr = dt.strftime(constants.TIME_FORMAT)
                try:
                    d[constants.HOSTNAME_TIME_MAP[hostname]] = dt
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

    def __processing_porocessors(self, mail: dict, responsibility: str) -> ProcessorAction:
        if self._pluginManager is not None:
            chain = self._pluginManager.get_chain_with_responsibility(responsibility)
            if chain is not None:
                pd = ProcessorData(mail)
                chain.process(pd)
                return pd.action

    def __preprocessing(self, mail: dict) -> ProcessorAction:
        """Apply preprocessing plugins to a mail-object."""
        return self.__processing_porocessors(mail, 'preprocessors')

    def __postprocessing(self, mail: dict) -> ProcessorAction:
        """Apply postprocessing plugins to a mail-object."""
        return self.__processing_porocessors(mail, 'postprocessors')

    def __process_aggregated_mail(self, mail: dict) -> None:
        isIncomplete = True

        tags = mail.get('tags')
        if isinstance(tags, list):
            if 'incomplete' not in tags:
                isIncomplete = False

        if isIncomplete:
            scope = SearchScope.INCOMPLETE
        else:
            scope = SearchScope.COMPLETE


        if not Config().get('noprint'):
            if not Config().get('onlyprintmsgs'):
                pprint(mail)

            if not isinstance(self.__build_final_metadata.get('aggregatedmails'), int):
                self.__build_final_metadata['aggregatedmails'] = 1
            else:
                self.__build_final_metadata['aggregatedmails'] += 1

            sys.stdout.write('\rAggregated %d mails' % self.__build_final_metadata['aggregatedmails'])
            sys.stdout.flush()

        self._repository.insert_or_update(mail, scope)

    def __aggregate_mails(self,
                          fragmentChain: List[Dict[str, dict]],
                          keyChain: List[str]) -> None:
        """
        Abstract:
        This method aggregates all fragments with a fragmentChain
        which is defined by the keyChain.

        Description:
        fragments:
        Dictionary which maps a given ID to a fragment,
        eg. self._map_qid_mxin

        fragmentChain:
        the given fragments have to be aggregated with other fragments,
        those other fragments are found in the fragmentChain:

        eg. a fragmentChain may contain self._map_qid_mxin and self._map_msgid
        this would mean that the given fragments are first aggregated with
        self._map_qid_imap and then with self._map_msgid

        keyChain:
        in order to aggregate the fragments with a fragmentChain
        the algorithm has to know which keys are relevant for aggregating.
        Those keys are defined in the keyChain, the keyCHain must have
        the same amount of elements as the fragmentChain --> each fragments
        in the fragmentChain is mapped using one key in the keyChain

        eg.
        fragmentChain = [ self._map_qid_imap,     self._map_msgid     ]
        keyChain      = [ constants.PHD_IMAP_QID, constants.MESSAGEID ]

        a given key is now used to find a given fragment in the fragmentChain:

        we will start with the first key:
        index = 1

        frags     = fragmentChain[index]
        key       = keyChain[index]

        now the key is used to extract a given fragment out of frags:

        fragment = fragments[key]

        this fragment is then merged with one fragment in fragments.
        """

        """
        Clojures
        """

        def agg_wrapp(frag: dict) -> dict:
            """
            Wrapper function for aggregating the fragments.

            This function is needed, as a fragment may be a list, see below.
            """


            # create aggregate target
            # all data is aggregated into this dict
            initialID = frag.get(keyChain[0])

            builder = ExpressionBuilder()
            builder.add_field(ExpressionField(keyChain[0], str(initialID), Comparator.equal))

            do_query = partial(self._repository.find, builder.expression)

            # if we are currently merging the messageid map and we
            # already have merged this messageid we will ignore it
            if keyChain[0] == constants.MESSAGEID and \
                            self.__build_final_metadata.get(initialID) is not None:
                raise AlreadyInRepository()

            if initialID == constants.NOQUEUE:
                builder2 = ExpressionBuilder()

                for k, v in frag.items():
                    builder2.add_field(ExpressionField(k, v, Comparator.regex_i))

                if len(self._repository.find(builder2.expression, SearchScope.ALL)) > 0:
                    raise AlreadyInRepository()

                target = copy.deepcopy(frag)
            else:
                try:
                    target = next(do_query(SearchScope.INCOMPLETE))
                    self._repository.remove_metadata(target)
                    self.__preprocessing(target)

                    # remove this data as it may be complete afterwards
                    self._repository.delete(builder.expression, SearchScope.INCOMPLETE)
                except StopIteration as e:
                    res = do_query(SearchScope.COMPLETE)
                    if len(res) > 0:

                        res = next(res)

                        for i in range(1, len(keyChain)):
                            try:
                                del fragmentChain[i][res.get(keyChain[i])]
                            except Exception as e:
                                continue

                        raise AlreadyInRepository()

                    target = copy.deepcopy(frag)

            # the current fragment is now copied to the target
            # so we can start merging the fragmentChain:

            # we will iterate over the keyChain, as we want to aggregate
            # the fragment in order of succession
            for index in range(1, len(keyChain)):
                # extract the data given by a key
                # in the keyChain from the target
                nextid = target.get(keyChain[index])

                # create a list for all fragments which has been aggregated
                # and can be deleted afterwards
                toDelete = []

                # if the target contains key data, we will use it to for aggregation
                if nextid is not None:
                    def agg_nextid(id):
                        """An id may be a list, so we need a clojure, see below."""

                        # get the fragment stored with the 'id'
                        otherFrag = fragmentChain[index].get(id)
                        if otherFrag is not None:
                            # if the fragment is not None (aka if it exists)
                            # we will merge it with the target

                            builder = ExpressionBuilder()
                            builder.add_field(ExpressionField(keyChain[index], id, Comparator.equal))

                            do_query = partial(self._repository.find, builder.expression)

                            def gather_existing_data(scope: SearchScope):
                                try:
                                    data = next(do_query(scope))
                                    self._repository.remove_metadata(data)
                                    self.__preprocessing(data)
                                    self._merge_data(target, data)

                                    self._repository.delete(builder.expression, scope)
                                except StopIteration as e:
                                    pass

                            gather_existing_data(SearchScope.INCOMPLETE)
                            # gather_existing_data(SearchScope.COMPLETE)

                            self._merge_data(target, otherFrag)

                            if keyChain[index] == constants.MESSAGEID:
                                # if the current id is the messageid
                                # we will store it as we dont need to merge
                                # it again later (last phase in build_final)
                                self.__build_final_metadata[id] = True
                            else:
                                # we can not delete the merged fragment now, as it would
                                # break the iteration, so we have to cache its indexes
                                toDelete.append(
                                    (index, id)
                                )

                    if isinstance(nextid, list):
                        # if the extracted id is a list, then we will
                        # iterate over it.
                        # eg. For some reason there may be
                        # multiple queueids (edge case)
                        for n in nextid:
                            agg_nextid(n)
                    else:
                        # if the is not a list, then we do not iterate over it
                        agg_nextid(nextid)

                    # when we are finished with the current fragmentChain, we will
                    # delete all fragments which we aggregated
                    for id1, id2 in toDelete:
                        del fragmentChain[id1][id2]
                else:
                    # if not then we will continue with the next key
                    continue

            return target

        def process(target: dict):
            # process all the edge cases
            data = MailEdgeCaseProcessorData(
                target,
                self._map_qid_mxin,
                self._map_qid_imap,
                self._map_msgid,
                self._map_pickup,
                self._merge_data,
                keyChain[0]
            )

            chain = self._pluginManager.get_chain_with_responsibility('mail-edge-cases')
            chain.process(data)

            if self.__postprocessing(target) != ProcessorAction.DELETE:
                self.__process_aggregated_mail(target)

        """
        Procedure start
        """

        # as we want to aggregate each fragment in fragments with some fragments
        # in the fragmentChain given by the keys in the keyChain we will iterate
        # over the fragments:
        for id, frag in fragmentChain[0].items():
            # if the fragment is a list then we need to iterate over
            # this list, as the actual fragments are in this list
            # This happens when multiple fragments have the same id
            # in the case of NOQUEUE (rejected mails)
            if isinstance(frag, list):
                for f in frag:
                    try:
                        process(agg_wrapp(f))
                    except AlreadyInRepository as e:
                        continue

            else:
                # if the fragment is not a list, then it is
                # a dict, so we can just aggregate it
                try:
                    process(agg_wrapp(frag))
                except AlreadyInRepository as e:
                    # if we already stored this fragment in the repo
                    # we will continue with the next
                    continue

        # all fragments have been aggregated now, we will therefore
        # clear the list of fragments
        fragmentChain[0].clear()

    def build_final(self) -> None:
        """Aggregate data to mail objects."""
        self.__build_final_metadata = {}

        self.__aggregate_mails(
            [
                self._map_qid_mxin,
                self._map_qid_imap,
                self._map_msgid
            ],
            [
                constants.PHD_MXIN_QID,
                constants.PHD_IMAP_QID,
                constants.MESSAGEID
            ]
        )

        self.__aggregate_mails(
            [
                self._map_qid_imap,
                self._map_msgid
            ],
            [
                constants.PHD_IMAP_QID,
                constants.MESSAGEID
            ]
        )

        self.__aggregate_mails(
            [
                self._map_msgid,
            ],
            [
                constants.MESSAGEID
            ]
        )

        for id, mail in self._map_pickup.items():

            builder = ExpressionBuilder()
            builder.add_field(ExpressionField(constants.PHD_IMAP_QID, id, Comparator.equal))

            if len(self._repository.find(builder.expression,SearchScope.ALL)) == 0:
                if self.__postprocessing(mail) != ProcessorAction.DELETE:
                    self.__process_aggregated_mail(mail)

        self._map_pickup.clear()

        if not Config().get('noprint'):
            print('')

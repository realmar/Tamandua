"""Module which contains metadata classes for mail edge case processors."""

from argparse import Namespace
from typing import Callable

from .plugin_processor import ProcessorData


class MailEdgeCaseProcessorData(ProcessorData):
    """Store the data needed for the mail edge case processors."""

    def __init__(self,
                 mail: dict,
                 map_qid_mxin: dict,
                 map_qid_imap: dict,
                 map_msgid: dict,
                 map_pickup : dict,
                 merge_data: Callable[[dict, dict], None],
                 origin: str):
        """Constructor of MailEdgeCaseProcessorData."""

        super().__init__(Namespace(
            mail=mail,
            map_qid_mxin=map_qid_mxin,
            map_qid_imap=map_qid_imap,
            map_msgid=map_msgid,
            map_pickup=map_pickup,
            merge_data=merge_data,
            origin=origin
        ))

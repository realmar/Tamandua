"""
Contains globally used constants.

Those constants represent domain specific elements in Tamandua, which 
should be stored centrally to ensure consistency.

If you are writing plugins: please use those constants when defining
domain specific stuff. (eg. in regexps)
"""


# Hostnames

PHD_MXIN = 'phdmxin'
PHD_IMAP = 'phdimap'

# Queue ID

PHD_MXIN_QID = PHD_MXIN + '_qid'
PHD_IMAP_QID = PHD_IMAP + '_qid'

HOSTNAME_QID = 'hostname_qid'

NOQUEUE = 'NOQUEUE'

# Message ID

MESSAGEID = 'messageid'

# Time

PHD_MXIN_TIME = PHD_MXIN + '_time'
PHD_IMAP_TIME = PHD_IMAP + '_time'

TIME_FORMAT = '%Y/%m/%d %H:%M:%S'

HOSTNAME_TIME_MAP = {
    PHD_MXIN: PHD_MXIN_TIME,
    PHD_IMAP: PHD_IMAP_TIME
}

# Log

LOGLINES = 'loglines'

# Integrity

COMPLETE = 'complete'
DESTINATION = 'destination'

DESTINATION_DELIVERED = 'delivered'
DESTINATION_REJECT = 'reject'
DESTINATION_HOLD = 'hold'
DESTINATION_VIRUS = 'virus'
DESTINATION_OTHER = 'other'
DESTINATION_UNKOWN = 'unknown'

# config

CONFIGFILE = 'config.json'

# environment variables

TAMANDUAENV = 'TAMANDUAENV'
DEVENV = 'development'
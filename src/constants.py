"""
Contains globally used constants.

Those constants represent domain specific elements in Tamandua, which 
should be stored centrally to ensure consistency.

If you are writing plugins: use those constants when defining
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

# User

USERNAME = 'username'
UID = 'uid'

# Time

PHD_MXIN_TIME = PHD_MXIN + '_time'
PHD_IMAP_TIME = PHD_IMAP + '_time'

def get_all_times():
    return (PHD_MXIN_TIME, PHD_IMAP_TIME)

TIME_FORMAT = '%Y/%m/%d %H:%M:%S'

HOSTNAME_TIME_MAP = {
    PHD_MXIN: PHD_MXIN_TIME,
    PHD_IMAP: PHD_IMAP_TIME
}

# delivery

DELIVERYRELAY = 'deliveryrelay'
DELIVERYMESSAGE = 'deliverymessage'

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

# domain specific data

DPHYS_DOMAINS = [
    'aglpl.ch',
    'chipp.ch',
    'comp-phys.org',
    'first.ethz.ch',
    'ihp.phys.ethz.ch',
    'iqe.phys.ethz.ch',
    'itp.phys.ethz.ch',
    'lists.comp-phys.org',
    'lists.phys.ethz.ch',
    'mail.phys.ethz.ch',
    'openqu.org',
    'particle.phys.ethz.ch',
    'paulicenter.ch',
    'phd-mxin.ethz.ch',
    'phys.ethz.ch',
    'physiklaborant.ch',
    'qipc2011.ethz.ch',
    'solid.phys.ethz.ch',
    'stat-phys.org',
    'stud.phys.ethz.ch',
    'bb.phys.ethz.ch',
    'rt.phys.ethz.ch',
    'astro.phys.ethz.ch'
]

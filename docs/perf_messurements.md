Perf Messurements
=================

Tamandua Version: Commit: `165ac580959ef1e1d9c8f8281f8a2e1291acd0b7`

Taken: 28.06.2017

1
-

mail.log-20170330
367722946 : 351M

cmd: `/usr/bin/time -v python3 tamandua_parser.py /scratch/log/mail.log-20170330 --no-print`

Note: we will not use the shell built-in `time`.

```sh
Elapsed (wall clock) time (h:mm:ss or m:ss): 2:55.45
Maximum resident set size (kbytes): 1077360

Elapsed (wall clock) time (h:mm:ss or m:ss): 2:53.78
Maximum resident set size (kbytes): 1075000

Elapsed (wall clock) time (h:mm:ss or m:ss): 2:59.01
Maximum resident set size (kbytes): 1077788
```

Object Store size: 203 MB

2
-

mail.log-20170425
177606019 : 170M

cmd: `/usr/bin/time -v python3 tamandua_parser.py /scratch/log/mail.log-20170425 --no-print`

Note: we will not use the shell built-in `time`.

```sh
Elapsed (wall clock) time (h:mm:ss or m:ss): 1:23.44
Maximum resident set size (kbytes): 480924

Elapsed (wall clock) time (h:mm:ss or m:ss): 1:20.71
Maximum resident set size (kbytes): 485380

Elapsed (wall clock) time (h:mm:ss or m:ss): 1:23.19
Maximum resident set size (kbytes): 485472
```

Object Store size: 86 MB
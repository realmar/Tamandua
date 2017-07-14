Perf Messurements One
=====================

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

Perf Messurements Two
=====================

Before rejected mail were indexed
---------------------------------

Tamandua Version: Commit: `6be2f062b6343d3a8d3fe9e2a58a4c0510b44679`

Taken: 14.06.2017

mail.log-20170713
135412146 : 130M

### First run

DB is empty all data is written

```sh
(ve) amartako@ash:~/Documents/Projects/IPA/Tamandua (master)$ /usr/bin/time -v ./tamandua_parser.py --print-msgs /scratch/mail.log-20170713
Processed 909713 lines
Aggregated 29639 mails

	Elapsed (wall clock) time (h:mm:ss or m:ss): 7:36.10
	Maximum resident set size (kbytes): 152648
```

### Second run

DB is full, some data will get rewritten (incomplete), also there are way too many mail objects rewritten. This is the result of not being able to match the correct mail objects.

```sh
(ve) amartako@ash:~/Documents/Projects/IPA/Tamandua (master)$ /usr/bin/time -v ./tamandua_parser.py --print-msgs /scratch/mail.log-20170713
Processed 909713 lines
Aggregated 1251 mails

	Elapsed (wall clock) time (h:mm:ss or m:ss): 13:55.36
	Maximum resident set size (kbytes): 151612
```

In short, it takes insanely long ..

After rejected mail were indexed
--------------------------------

Tamandua Version: Commit: `a9e6cc9da4017b79938e1f44afdeb6411319b33a`

Taken: 14.06.2017

mail.log-20170713
135412146 : 130M

### First run

DB is empty all data is written

```sh
(ve) amartako@ash:~/Documents/Projects/IPA/Tamandua (master)$ /usr/bin/time -v ./tamandua_parser.py --print-msgs /scratch/mail.log-20170713
Processed 909713 lines
Aggregated 29639 mails

	Elapsed (wall clock) time (h:mm:ss or m:ss): 6:05.94
	Maximum resident set size (kbytes): 152612
```

### Second run

DB is full, some data will get rewritten (incomplete), as you can see under 60 mail are rewritten, this means that, not only is the parser faster by a huge margin but also matches the mail objects better.

```sh
(ve) amartako@ash:~/Documents/Projects/IPA/Tamandua (master)$ /usr/bin/time -v ./tamandua_parser.py --print-msgs /scratch/mail.log-20170713
Processed 909713 lines
Aggregated 52 mails

	Elapsed (wall clock) time (h:mm:ss or m:ss): 0:48.56
	Maximum resident set size (kbytes): 151728
```
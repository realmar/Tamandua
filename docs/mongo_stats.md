Following Logfile

```sh
mail.log-20170425
177606019     170M
```

generates following data volume in mongodb:

```sh
> use tamandua
switched to db tamandua
> db.stats()
{
	"db" : "tamandua",
	"collections" : 3,
	"views" : 0,
	"objects" : 23269,
	"avgObjSize" : 2216.2841548841807,
	"dataSize" : 51570716,
	"storageSize" : 21180416,
	"numExtents" : 0,
	"indexes" : 3,
	"indexSize" : 307200,
	"ok" : 1
}
```

The given values are in `Bytes`.
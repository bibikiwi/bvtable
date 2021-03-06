# bvtable

Table format overview of your crypto assets in bitvavo.
With output format for ascii, ansi color, unicode chars, conky colors, etc...

# Requirements

```
pip install python-bitvavo-api
pip install pytz
```

# settings file

You can put a settings file in any of the following paths :

```
~/.bvtablerc.json
./bvtablerc.json
```

or provide it on the command line with the -f options

It should contain at least an API key for bitvavo.

This app does not do any transactions, so the safest is to use a view-only key here.

An example can be found in the examples folder

```
cp examples/bvtablerc.json-EXAMPLE ~/.bvtablerc.json
```

add your keys

```
{
	"apikey": "<bitvavo api key (RO)>",
	"apisecret": "<bitvavo api key secret>"

}
```

# examples


simple output for terminals that can do nothing

```
./bvtable.py
```

![alt text](https://github.com/bibikiwi/bvtable/blob/main/doc/001-simple.png?raw=true)

square brackets instead of borders
```
./bvtable.py -b vhk
```

![alt text](https://github.com/bibikiwi/bvtable/blob/main/doc/002-square.png?raw=true)


full ansii color output with utf8 symbols and unicode borders
```
./bvtable.py -b unicode -s utf8 -c ansii
```

![alt text](https://github.com/bibikiwi/bvtable/blob/main/doc/003-coloransiutf8.png?raw=true)


with conky colors and font headers
```
./bvtable.py -b unicode -c conky -m conky -b unicode
```
an example conkyrc file can be found in the examples folder

![alt text](https://github.com/bibikiwi/bvtable/blob/main/doc/004-conky.png?raw=true)
	

#!/usr/bin/python3

###=== IMPORTS ===###

import os
import sys
import json
import time
import datetime,pytz
from python_bitvavo_api.bitvavo import Bitvavo

###=== GLOBAL ===###

options = {}

###=== SETTINGS ===###

#add more profiles in your settingsfile
profiles = {
		'conky': {
				'border'	: 'unicode',
				'color'		: 'conky',
				'mode'		: 'conky'
			},
		'dos': {
				'color'		: 'ansii',
				'border'	: 'unicode',
				'symbols'	: 'simple',
				'mode'		: 'win'
			}
	}


default_options = {
		'basecur'	: 'EUR',		#The base currency
		'color'		: 'none',		#method to generate color
		'border'	: 'text',		#for unicode border characters (vierkante haakjes)
		'symbols'	: 'simple',		#for arrows or +/-
		'mode'		: 'text',		#conky for setting font, base color,...
		'order'		: 'symbol',		#Order the table by x
		'reverse'	: 'false',		#Order direction
		'file'		: None,
		'fieldorder'	: [
					'symbol',
					'daily_low',
					'daily_low_historic',
			                'daily_high',
					'daily_high_historic',
				 	'last',
			                'last_low_historic',
					'last_high_historic',
					'change_24h',
			                'value',
					'paid',
					'gain',
			                'wallet',
					'symbol',
					'trend24h'
				]
		}

shorts = {
		'c': ['color'		,('none','conky','ansii')		],
		'b': ['border'		,('ascii','unicode','vkh','conky')	],	#vkh = square brackets
		's': ['symbols'		,('simple','utf8','num')		],
		'm': ['mode'		,('text','conky','win')			],
		'o': ['order'		,None					],
		'r': ['reverse'		,('true','false')			],
		'p': ['profile'		,None					],
		'f': ['file'		,None					]
	}

class codes:
  ansii_reset	= '\033[0m'
  ansii_bold	= '\033[1m'
  ansii_dim	= '\033[2m'
  ansii_red	= '\033[31m'
  ansii_magenta = '\033[95m'
  ansii_cyan    = '\033[96m'
  ansii_yellow	= '\033[33m'
  ansii_white	= '\033[37m'
  ansii_test1	= '\033[39m'
  ansii_OKBLUE	= '\033[94m'
  ansii_green	= '\033[92m'
  conky_red	= '${color4}'
  conky_white	= '${color8}'
  conky_reset	= '${color2}'
  conky_yellow	= '${color3}'
  conky_green	= '${color1}'
  conky_font	= '${font Nimbus Mono PS:size=24}'
  conky_font2	= '${font Ubuntu Mono:size=24}'
  conky_font3	= '${font Terminus Mono:size=24}'


###=== Functions ===###

def alignment(field,widths):
  return f"%{ widths[field]*(-1 if datafields[field][1]=='L' else 1) }s"

def fh_plain(mode,fieldvalue,field,w):
  fieldvalue = f"{ fieldvalue }{ datafields[field][2] }"
  width = len(fieldvalue)
  if mode == 'w':
    return width
  else:
    return fieldvalue

def fh_histo(mode,fieldvalue,field,widths):
  fieldvalue1 = f"{ fieldvalue }{ datafields[field][2] }"
  if mode == 'w':
    width = len(fieldvalue1)
    return width
  else:
    fieldvalue2 = alignment(field,widths) % fieldvalue1
    if options['color'] == 'conky':
      if fieldvalue=='!' or fieldvalue>15:
        fieldvalue2 = codes.conky_yellow + fieldvalue2 + codes.conky_reset
    elif options['color'] == 'ansii':
      if fieldvalue=='!' or fieldvalue>15:
        fieldvalue2 = codes.ansii_yellow + fieldvalue2 + codes.ansii_magenta
    return fieldvalue2

def fh_twodec_nocol(mode,fieldvalue,field,widths):
  fieldvalue1 = "%.2f" % fieldvalue
  fieldvalue1 = f"{ fieldvalue1 }{ datafields[field][2] }"
  if mode =='w':
    width = len(fieldvalue1)
    return width
  else:
    fieldvalue2 = alignment(field,widths) % fieldvalue1
    return fieldvalue2

def fh_twodec(mode,fieldvalue,field,widths):
  fieldvalue1 = "%.2f" % fieldvalue
  fieldvalue1 = f"{ fieldvalue1 }{ datafields[field][2] }"
  if mode =='w':
    width = len(fieldvalue1)
    return width
  else:
    fieldvalue2 = alignment(field,widths) % fieldvalue1
    if options['color'] == 'conky':
      if fieldvalue<0:
        fieldvalue2 = codes.conky_red + fieldvalue2 + codes.conky_reset
      else:
        fieldvalue2 = codes.conky_green + fieldvalue2 + codes.conky_reset
    elif options['color'] == 'ansii':
      if fieldvalue<0:
        fieldvalue2 = codes.ansii_red + fieldvalue2 + codes.ansii_magenta
      else:
        fieldvalue2 = codes.ansii_green + fieldvalue2 + codes.ansii_magenta
    return fieldvalue2


def fh_trend(mode,fieldvalue,field,widths):
  if mode == 'w':
    width = len(fieldvalue)
    return width
  else:
    orig = fieldvalue

    #The symbols
    if options['symbols'] == 'utf8':
      t1 =  {	'1': u'\u2198',
		'2': u'\u2198',
		'3': u'\u2197',
		'4': u'\u2197',
		'?': '?'
  	}
      fieldvalue = ''.join([t1[c] for c in fieldvalue])
    elif options['symbols'] == 'simple':
      t1 = {	'1': 'M',
		'2': '-',
		'3': '+',
		'4': 'P',
		'?': '?'
	}
      fieldvalue = ''.join([t1[c] for c in fieldvalue])


    #The colors
    if options['color'] == 'conky':
        t1 =  {	'1': codes.conky_red,
		'2': codes.conky_reset,
		'3': codes.conky_green,
		'4': codes.conky_white,
		'?': ''
	}
        fieldvalue = (''.join([ (t1[orig[n]] + fieldvalue[n]) for n in range(0,len(orig))])) + codes.conky_reset
    elif options['color'] == 'ansii':
        t1 =  {	'1': codes.ansii_red,
		'2': codes.ansii_magenta,
		'3': codes.ansii_green,
		'4': codes.ansii_white,
		'?': ''
	}
        fieldvalue = (''.join([ (t1[orig[n]] + fieldvalue[n]) for n in range(0,len(orig))])) + codes.ansii_magenta

    fieldvalue += (' '*(widths[field]-len(orig)))

    return fieldvalue



#					title		,align	,unit	,fancyhandler
datafields = {
		'symbol'		:('Sym'		,'L'	,''	,fh_plain		),
		'open'			:('open'	,'R'	,''	,fh_plain		),
		'daily_low'		:('low'		,'R'	,'€'	,fh_plain		),
		'daily_low_historic'	:('HL'		,'R'	,''	,fh_histo		),
		'daily_high'		:('high'	,'R'	,'€'	,fh_plain		),
		'daily_high_historic'	:('HH'		,'R'	,''	,fh_histo		),
		'last'			:('last'	,'R'	,'€'	,fh_plain		),
		'last_low_historic'	:('HL'		,'R'	,''	,fh_histo		),
		'last_high_historic'	:('HH'		,'R'	,''	,fh_histo		),
		'change_24h'		:('chg24h'	,'R'	,'%'	,fh_twodec		),
		'value'			:('value'	,'R'	,'€'	,fh_twodec		),
		'paid'			:('paid'	,'R'	,'€'	,fh_twodec_nocol	),
		'gain'			:('gain'	,'R'	,'%'	,fh_twodec		),
		'wallet'		:('wallet'	,'R'	,''	,fh_plain		),
		'trend24h'		:('trend 24h'	,'R'	,''	,fh_trend		)
	}



###=== FUNCTIONS ===###

def loadsettings(params):
  '''Load a settingsfile, the one from command line or a default one'''
  settingsfiles = ['~/.bvtablerc.json','./bvtablerc.json']
  if 'f' in params:
    settingsfiles = [params['f']] + settingsfiles
  settings = {}
  for fname in settingsfiles:
    efname = os.path.expanduser(fname)
    if os.path.exists(efname):
      try:
        settings = json.load(open(efname,'r'))
      except exception as e:
        print(f"Error: Cannot load settings file [{efname}] : {efname}")
        sys.exit()
    else:
      if 'f' in params:
        print(f"Error: Settingsfile [{efname}] not found.")
        sys.exit()
  return settings



def dayasettingsfilesgo(num):
  nowtime = int(time.time())
  day = (nowtime // (60*60*24))
  da = day - num
  return da

def writedata(data,filename):
  prefix = '.'
  if 'dumppath' in options:
    prefix = options['dumppath']
  path = f"{ prefix }/{ filename }"
  json.dump(data,open(path,'w'),indent=4)

def lastlower(candles,value):
  result = '!'
  for candle in candles[1:]:		#skip last 24h ? --> [1:]
    if float(candle[3])<value:
      result = (int(time.time())-(candle[0]//1000))//(24*60*60)
      break
  return result

def lasthigher(candles,value):
  result = '!'
  for candle in candles[1:]:		#skip last 24h ? --> [1:]
    if float(candle[2])>value:
      result = (int(time.time())-(candle[0]//1000))//(24*60*60)
      break
  return result

def trendindicator(trenddata):
  (close,open) = trenddata
  rise = open<close
  force = abs(((open - close) / close) * 100)
  indicator = (4 if force>5.0 else 3) if open<close else (1 if force>5.0 else 2)
  return indicator

def trend(candles24h):
  hr_now = int(time.strftime("%H"))
  trend_str = [ '?' for x in range(12)]

  cnt = 0
  for (millis,open,hi,lo,close,kweni3) in candles24h[::-1]:
    hr = int(datetime.datetime.fromtimestamp(millis // 1000,pytz.utc).strftime("%H"))
    pos = (((hr + hr_now) // 2)+1) % 12
    #print("%2d - %02d UTC - %2d" % (cnt,hr,pos))
    trend_str[pos] = trendindicator((float(close),float(open)))
    cnt += 1

  trnd_str = ''.join( [ "%s" % x for x in trend_str ] )

  return trnd_str

def print_header(options):
  if options['mode'] in ['conky']:
    print(codes.conky_reset + codes.conky_font,end='')
  if options['color'] == 'ansii':
    print(codes.ansii_magenta,end='')
  if options['mode'] in ['win']:
    os.system('')


def fancify_records(records,options):
  #initialize widths
  widths = { t:len(datafields[t][0]) for t in datafields }
  #calculate the widths
  for record in records:
    for field in record:
      width = datafields[field][3]('w',record[field],field,widths)
      if width>widths[field]:
        widths[field]=width
  #fancify the records
  for recnum in range(0,len(records)):
    for field in records[recnum]:
      records[recnum][field] = datafields[field][3]('f',records[recnum][field],field,widths)
  return (records,widths)


def fieldliner(widths,fieldname,char_def,char_exc=None):
  line = char_def*widths[fieldname]
  if char_exc:
    if fieldname == 'trend24h':
      hr = int(datetime.datetime.fromtimestamp(int(time.time()),pytz.utc).strftime("%H"))
      pos = -(hr // 2)
      n = pos
      line = line[:n] + char_exc + line[n+1:]
  return line


def print_table_header(widths):
  if options['border'] == 'unicode':
    #The top line
    print(u'\u2554'+(u'\u2564'.join([ (u'\u2550'*widths[field]) for field in options['fieldorder'] ]))+u'\u2557')
    #The title line
    print(u'\u2551'+(u'\u2502'.join([ alignment(field,widths) % datafields[field][0] for field in options['fieldorder'] ]))+u'\u2551')
    #The title separator line
    print(u'\u2560'+(u'\u256a'.join([ fieldliner(widths,field,u'\u2550',u'\u2564') for field in options['fieldorder'] ]))+u'\u2563')
  elif options['border'] == 'vkh':
    #The title line
    print(''.join([ f"[{ alignment(field,widths) }]" % datafields[field][0] for field in options['fieldorder'] ]))
    #The title separator line
    print(''.join([ '-'*(2+widths[field]) for field in options['fieldorder'] ]))
  elif options['border'] == 'conky':
    #The title line
    print(''.join([ alignment(field,widths) % datafields[field][0] for field in options['fieldorder'] ]))
    #The title separator line
    print("${hr 2}")
  else:
    #The top line
    print('+'+(u'+'.join([ (u'-'*widths[field]) for field in options['fieldorder'] ]))+u'+')
    #The title line
    print('|'+(u'|'.join([ alignment(field,widths) % datafields[field][0] for field in options['fieldorder'] ]))+u'|')
    #The title separator line
    print('+'+(u'+'.join([ fieldliner(widths,field,u'-',u'+') for field in options['fieldorder'] ]))+u'+')


def print_table_footer(widths):
  #The bottom line
  if options['border'] == 'unicode':
    print(u'\u255a'+(u'\u2567'.join([ fieldliner(widths,field,u'\u2550',u'\u2567') for field in options['fieldorder'] ]))+u'\u255d')
  elif options['border'] == 'conky':
    print("${hr 2}")
  elif options['border'] in ['vkh','ascii']:
    print(''.join([ '-'*(2+widths[field]) for field in options['fieldorder'] ]))
  else:
    print('+'+(u'+'.join([ fieldliner(widths,field,u'-',u'+') for field in options['fieldorder'] ]))+u'+')


def order_records(records,options):
  return sorted(records, key=lambda x: x[options['order']], reverse=(options['reverse']=='true'))

def print_table(records,widths):
  print_table_header(widths)
  #for record in records:
  for record in records:
    if options['border'] == 'unicode':
      print(u'\u2551'+(u'\u2502'.join([ alignment(field,widths) % record[field] for field in options['fieldorder'] ]))+u'\u2551')
    elif options['border'] == 'vkh':
      print(''.join([ f"[{ alignment(field,widths) }]" % record[field] for field in options['fieldorder'] ]))
    else:
      print(u'|'+(u'|'.join([ alignment(field,widths) % record[field] for field in options['fieldorder'] ]))+u'|')

  print_table_footer(widths)


def calculate_totals(records):
  totals = {
		'paid': 0.0,
		'value': 0.0
	}
  for record in records:
    totals['paid'] += record['paid']
    totals['value'] += record['value']
  return totals

def print_endline(records,basecoin_data,start,limit,totals,options):
  ds = time.strftime("%Y-%m-%d %H:%M:%S")
  value = "%.2f" % totals['value']
  paid = "%.2f" % totals['paid']
  gainpct = ((totals['value']-totals['paid'])/totals['paid']) * 100
  gaintxt = "%.2f%%" % gainpct
  if options['color'] == 'conky':
    if gainpct<0:
      gaintxt = codes.conky_red + gaintxt + codes.conky_reset
    else:
      gaintxt = codes.conky_white + gaintxt + codes.conky_reset
  elif options['color'] == 'ansii':
    if gainpct<0:
      gaintxt = codes.ansii_red + gaintxt + codes.ansii_magenta
    else:
      gaintxt = codes.ansii_white + gaintxt + codes.ansii_magenta
  endline = []
  endline.append(f"{ ds }")
  endline.append(f"{ options['basecur'] }")
  endline.append(f"Avail: { basecoin_data['available'] }€")
  endline.append(f"Orders: { basecoin_data['inOrder'] }€")
  endline.append(f"Crypto: { value }€/{ paid }€ ({ gaintxt })")
  endline.append(f"Quota: { limit }")
  endline.append("API: %2.2fs" % (time.time()-start))
  print(' | '.join(endline))

def calculatepaid(trades):
  paid = 0.0
  for trade in trades:
    if 'fills' in trade:
      for fill in trade['fills']:
        if trade['side'] == 'buy':
          amount = float(fill['amount'])
          price  = float(fill['price'])
          fee    = float(fill['fee'])
          total = amount*price+fee
          paid += total
        elif trade['side'] == 'sell':
          amount = float(fill['amount'])
          price  = float(fill['price'])
          fee    = float(fill['fee'])
          total = amount*price-fee
          paid -= total
  return paid


def printhelp():
  print()
  print(f"{ sys.argv[0] } [-<opt1> <value1>] [-<optN> <valueN>] ...")
  for opt in shorts:
    sug = ""
    if shorts[opt][1]:
      sug = f"({ ','.join(shorts[opt][1]) })"
    print(f"  -{ opt } : ({ shorts[opt][0] }){sug}")
  print()


def parseparams():
  '''This just parses all parameters and ensures complete '-<letter> <value>' is given'''
  args = sys.argv[1:]
  params = {}
  while args:
    label = args.pop(0)
    if len(label)==2 and label[0] == '-':
      label = label[1]
      if label == 'h':
        printhelp()
        sys.exit()
      if args:
        value = args.pop(0)
        params[label] = value
      else:
        print(f"Error: There's no value for parameter '{ label }'")
        sys.exit()
    else:
      print(f"Error: parameter must start with '-' (offending:{ label })")
      sys.exit()
  return params


def parseoptions(settings,params):
  global options
  global profiles

  #add the eventual profiles from the settingsfile to the known available profiles
  if 'profiles' in settings:
    profiles = { **profiles,**settings['profiles'] }

  #construct the list of available values for the profile selection
  shorts['p'][1] = list(profiles.keys())

  #construct the list of available values for the order field
  shorts['o'][1] = list(datafields.keys())

  #initialize with the default options from the code
  options = default_options

  #update with the default options from the settingsfile
  if 'defaultprofile' in settings:
    options = {**options, **profiles[settings['defaultprofile']]}

  for param in params:
    if param in shorts:
      if shorts[param][1]:
        if not (params[param] in shorts[param][1]):
          print(f"Error: [{ params[param] }] is not a valid value for the [-{ param }] parameter. Valid = { ','.join(shorts[param][1]) }")
          sys.exit()
        if param == 'p':	#apply profile at that position in the commandline
          options = {**options, **profiles[params[param]]}
        options[shorts[param][0]] = params[param]

  if 'fieldorder' in settings:
    options['fieldorder'] = settings['fieldorder']

  if not 'apikey' in options:
    if 'apikey' in settings:
      options['apikey'] = settings['apikey']
    else:
      print("You need to povide an API key in the settings file.")
      sys.exit()

  if not 'apisecret' in options:
    if 'apisecret' in settings:
      options['apisecret'] = settings['apisecret']
    else:
      print("You need to povide an API secret in the settings file.")
      sys.exit()

  return options


###=== MAIN FUNCTION ===###


def main():
  global fieldorder

  #Record start time for duration measurement
  allstart = time.time()

  #construct the parameters for bitvavo
  bvoptions = {
	'APIKEY': options['apikey'],
	'APISECRET': options['apisecret'],
	'RESTURL': 'https://api.bitvavo.com/v2',
	'WSURL': 'wss://ws.bitvavo.com/v2/',
	'ACCESSWINDOW': 10000,
	'DEBUGGING': False
	}

  #initialize bitvavo class
  bitvavo = Bitvavo(bvoptions)

  #get general data from bitvavo
  balance = bitvavo.balance({})
  ticker24h = bitvavo.ticker24h({})

  #make data searchable per market
  markets24h = { t['market']:t for t in ticker24h }

  epoch_today  = int(time.time())
  epoch_1year  = epoch_today - (60*60*24*366)
  epoch_24h    = epoch_today - (60*60*24)
  start_ms_1y  = epoch_1year*1000
  start_ms_24h = epoch_24h*1000
  end_ms = epoch_today*1000

  records = []
  for coin in balance:
    symbol = coin['symbol']
    if symbol == options['basecur']:
      basecoin_data = coin
    else:
      record = {}
      available = coin['available']
      market = f"{symbol}-{ options['basecur'] }"
      trades = bitvavo.getOrders(market, {})							#the trades to calculate the paid amount
      candles = bitvavo.candles(market, '1d', { 'start':start_ms_1y, 'end':end_ms } )		#366 candles per 24h over 366 days
      candles24h = bitvavo.candles(market, '2h', { 'start':start_ms_24h, 'end':end_ms } )	#12 candles per 2h over 24h
      paid = calculatepaid(trades)								#calculate the paid amount per coin
      marketdata = markets24h[market]
      change = float(marketdata['last']) - float(marketdata['open'])
      chgval = change / float(marketdata['open']) * 100
      cryptovalue = float(marketdata['last'])*float(available)
      gain = ((cryptovalue - paid) / paid) * 100

      #writedata(trades,f"{ market }.trades")			#debug
      #writedata(candles,f"{ market }.1y.candles")		#debug
      #writedata(candles24h,f"{market}.24h.candles")		#debug
      #writedata(marketdata,f"{ market }.24h.marketdata")	#debug

      #create a record for this coin
      record['symbol'] = symbol
      record['open'] = marketdata['open']
      record['daily_low'] = marketdata['low']
      record['daily_low_historic'] = lastlower(candles,float(marketdata['low']))
      record['daily_high'] = marketdata['high']
      record['daily_high_historic'] = lasthigher(candles,float(marketdata['high']))
      record['last'] = marketdata['last']
      record['last_low_historic'] = lastlower(candles,float(marketdata['last']))
      record['last_high_historic'] = lasthigher(candles,float(marketdata['last']))
      record['change_24h'] = chgval
      record['value'] = cryptovalue
      record['paid'] = paid
      record['gain'] = gain
      record['wallet'] = available
      record['trend24h'] = trend(candles24h)

      #add the record
      records.append(record)

  print_header(options)
  totals = calculate_totals(records)
  records = order_records(records,options)
  (records,widths) = fancify_records(records,options)
  print_table(records,widths)
  limit = bitvavo.getRemainingLimit()
  print_endline(records,basecoin_data,allstart,limit,totals,options)



if __name__ == '__main__':
  params = parseparams()			#just parse the params into a dict
  settings = loadsettings(params)		#load the settings file, eventually use params['f'] value
  parseoptions(settings,params)			#check and apply the options
  main()					#the main thing




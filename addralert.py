#!/usr/bin/env python2


import sys
import json
import time
import subprocess
import argparse
import smtplib

def subp_call(cmdline):
 p = subprocess.Popen(cmdline, stdout=subprocess.PIPE,stderr=subprocess.PIPE)
 stdout_text = p.stdout.read()
 stderr_text = p.stderr.read()
 text = stdout_text + stderr_text
 if p.wait() != 0:
  print 'Error: bitcoin-cli...'
  print ' '.join(cmdline)
  print text
  sys.exit(-1)
 return stdout_text.strip() 

# your email credentials (uses TLS, port 587)
myemailserver='<email server>'  #smtp email server, e.g. smtp.gmail.com
myemaillogin='<login>' #your email server login, usually your email address
myemailpasswd='<passwd>' #password for email server login  
myemailfrom='<email addr from>' #your e-mail address
myemailto='<email addr to>' #the e-mail address you want to send the alert (can be your email address) 


parser = argparse.ArgumentParser()
parser.add_argument('addr', type=str,help="Address to match")
parser.add_argument('-t',action='store_true', default=False, dest='test', help='Test mode to check first block & send email')
args = parser.parse_args()

blockcount = int(subp_call(['bitcoin-cli', 'getblockcount']))
blockcountlast = blockcount-1
while 1:
 if args.test: blockcountlast = 0 # test
 else: blockcount = int(subp_call(['bitcoin-cli', 'getblockcount']))
  
 if blockcountlast == blockcount:
  time.sleep(300) # check every 5 minutes for new block
 else: 
  blockcountlast += 1
 
  print 'Processing block: '+str(blockcountlast)
  blockhash = subp_call(['bitcoin-cli', 'getblockhash', str(blockcountlast)])
  block = subp_call(['bitcoin-cli', 'getblock', blockhash, '2'])
#parse block
  blockjson  = json.loads(block)
  for tx in blockjson['tx']:
   for vout in tx['vout']:
    scriptPubKey = vout['scriptPubKey']
    if scriptPubKey['type'] != 'nulldata' and scriptPubKey['type'] != 'nonstandard':
     for addr in scriptPubKey['addresses']:
      if args.test: args.addr = '12c6DSiU4Rq3P4ZxziKxzrL5LmMBrzjrJX'
      if addr == args.addr:
       text = 'Address '+addr+' used in block '+str(blockcountlast)+' as output' 
       print text
       mail = 'Subject: '+text 
#send email
       emailserver = smtplib.SMTP(myemailserver, 587)
       emailserver.starttls()
       emailserver.login(myemaillogin, myemailpasswd)
       emailserver.sendmail(myemailfrom, myemailto, mail)
       emailserver.quit()
   
       if args.test: sys.exit(0)







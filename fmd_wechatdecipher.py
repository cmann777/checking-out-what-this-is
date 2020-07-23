from os.path import isfile
from pysqlcipher import dbapi2 as sqlite
import hashlib
import sys
import time
import logging
import re

SCRIPTNAME = "fmd_wechatdecipher.py"
logging.basicConfig(filename='EnMicroMsg-decrypted.log', format="%(asctime)s %(levelname)s: %(message)s", datefmt="%d-%b-%Y %I:%M:%S %p", level=logging.DEBUG)

def decrypt( key ):
	logging.info( "Connecting database..." )
	conn = sqlite.connect( "EnMicroMsg.db" )
	c = conn.cursor()		
	c.execute( "PRAGMA key = '" + key + "';" )
	c.execute( "PRAGMA cipher_use_hmac = OFF;" )
	c.execute( "PRAGMA cipher_page_size = 1024;" )
	c.execute( "PRAGMA kdf_iter = 4000;" )
	try:
		logging.info( "Decrypting..." )
		c.execute( "ATTACH DATABASE 'EnMicroMsg-decrypted.db' AS wechatdecrypted KEY '';" )
		c.execute( "SELECT sqlcipher_export( 'wechatdecrypted' );" )
		c.execute( "DETACH DATABASE wechatdecrypted;" )
		logging.info( "Detaching database..." )
		c.close()
		status = 1
	except:
		c.close()
		status = 0
	return status
	
	
def generate_key():
	imei = input( "IMEI: " )
	logging.info( "IMEI: " + str( imei ))
	uin = get_uin()
	logging.info( "UIN: " + str( uin ))
	logging.info( "Generating key..." )	
	key = hashlib.md5( str( imei ) + str( uin )).hexdigest()[ 0:7 ]
	logging.info( "Key: " + key )
	return key
	

def db_hash():
	f = open( 'EnMicroMsg-decrypted.db', 'rb' ).read()
	logging.info( "Generating hash values..." )	
	if len( f ) > 0:
		db_md5 = hashlib.md5( f ).hexdigest()
		logging.info( "EnMicroMsg-decrypted.db MD5: " + db_md5 )
		db_sha1 = hashlib.sha1( f ).hexdigest()
		logging.info( "EnMicroMsg-decrypted.db SHA1: " + db_sha1 )
		return
		

def get_uin():
	f = open( 'system_config_prefs.xml', 'r' ).read()
	uin = re.findall( 'name="default_uin" value="([\-?[0-9]+)"', f )
	return uin[ 0 ] if uin else 0


def main():	
	if not ( isfile( "EnMicroMsg.db" ) and isfile( "system_config_prefs.xml" )):
		print "##########"
		print "'EnMicroMsg.db' or 'system_config_prefs.xml' not found!"
		print "Script exiting..."
		print "##########"
		sys.exit()
		
	logging.info( "Script starting..." )
	key = generate_key()
	status = decrypt( key )
	if status == 1:
		db_hash()
		print "##########"
		print "Decryption successful!"
		print "Decrypted file: EnMicroMsg-decrypted.db"
		print "Log file: EnMicroMsg-decrypted.log"
		print "##########"
		logging.info( "Decryption successful!" )
		logging.info( "Decrypted filename: EnMicroMsg-decrypted.db" )
	else:
		print "##########"
		print "Decryption failed!"
		print "Make sure you input correct IMEI number!"
		print "Log file: EnMicroMsg-decrypted.log"
		print "##########"
		logging.info( "Decryption failed!" )
		logging.warning( "Make sure you input correct IMEI number!" )
	logging.info( "Script exiting..." )


main()
#!/usr/bin/python

from ConfigParser import SafeConfigParser
from datetime import datetime
import calendar
import tarfile,os,glob,string,subprocess,time,sys
import logging

Current_date_time = datetime.now().strftime("%Y-%m-%d") + "-" + str(calendar.timegm(time.gmtime())) 

LOGGER = logging.getLogger('BackMe')
LOG = logging.FileHandler('BackMe.log')
LOGGER.setLevel(logging.INFO)

FORMAT = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
LOG.setFormatter(FORMAT)

LOGGER.addHandler(LOG)

parser = SafeConfigParser()
parser.read ('archive_config.ini')
main_directory =  parser.get('basic_conf', 'parent_directory')
depth  = parser.get ('basic_conf', 'depth')
modified = parser.get ('basic_conf', 'modified')
tar_location = parser.get ('basic_conf', 'tar_location')
host_name = parser.get ('basic_conf', 'host_ip')
path_name = parser.get ('basic_conf','tarsave_path')
user_name = parser.get ('basic_conf','use_name')
rootDir = main_directory

def process_execute(command):
        proc = subprocess.Popen(command,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
       	output,error = proc.communicate()
	return output,error	

find_list_cmd = "find "+ rootDir +" -maxdepth "+depth+" -mindepth "+depth+" -type d -mtime " + modified

LOGGER.info('PREPARING THE TAR WITH %s' % (find_list_cmd))
compute_out = process_execute(find_list_cmd)

if compute_out == "":
	LOGGER.info('TAR FAILS, THERE IS NO FILE IN TAR ')
        print "Sorry No folders exists at the given search location"
        sys.exit(3)

folders_to_tar = compute_out[0].rstrip('')

l = folders_to_tar.split('\n')

tar = tarfile.open('%s/BackMe_%s.tgz' % (tar_location,Current_date_time),'w:gz')

LOGGER.info ('PREPARING THE TAR')

for name in l[0:-1]:
	print name
	tar.add(name)
tar.close()	

LOGGER.info ('TAR IS DONE WITH THE NAME BackMe_%s IN THE LOCATION %s' % (Current_date_time,tar_location))

LOGGER .info ('STARTING THE SCP PROCESS')

process_execute('scp %s/BackMe_%s.tgz %s@%s:%s' % (tar_location,Current_date_time,user_name,host_name,path_name))

LOGGER.info ('SCP IS DONE WITH THE USERNAME %s AND THE HOSTNAME %s ON THE REMOTE LOCATION %s'  % (user_name,host_name,path_name))

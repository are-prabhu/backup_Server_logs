#!/usr/bin/python

from ConfigParser import SafeConfigParser
from datetime import datetime
import calendar
import tarfile,os,glob,string,subprocess,time,sys
from logging import handlers

today = time.strftime("%Y-%m-%d")
backup_date = today
DEVNULL = open(os.devnull, 'wb')

parser = SafeConfigParser()
parser.read('archive_config.ini')

main_directory =  parser.get('basic_conf', 'parent_directory')
depth  = parser.get('basic_conf', 'depth')
modified = parser.get('basic_conf', 'modified')
tar_location = parser.get('basic_conf', 'tar_location')

if not os.path.exists(tar_location):
        os.makedirs(tar_location)
rootDir = main_directory

def process_execute(command):
        proc = subprocess.Popen(command,shell=True,stdout=subprocess.PIPE)
        output,error = proc.communicate()
        return output,error

def get_disk_size(folder):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(folder):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    return total_size

def split_the_path(path):
  allparts = []
    while 1:
        parts = os.path.split(path)
        if parts[0] == path:
            allparts.insert(0, parts[0])
            break
        elif parts[1] == path:
            allparts.insert(0, parts[1])
            break
        else:
            path = parts[0]
            allparts.insert(0, parts[1])
    return allparts

# tar tzvf 19-03-2014-po.tar | awk '{i+=$3} END{print (i/1024/1024) "MB"}'
find_list_cmd = "find "+ rootDir +" -maxdepth "+depth+" -mindepth "+depth+"  -type d -mtime "+ "+" + modified
(compute_out, compute_err) = process_execute(find_list_cmd)

if compute_out == "":
        print "Sorry No folders exists at the given search location"
        sys.exit(3)
folders_to_tar =  compute_out.rstrip()

#print folders_to_tar
l = folders_to_tar.split('\n')
for folders in l:
        folder_size = get_disk_size(folders)
        ls_command = "ls -al "+ folders
        ls_output,ls_error = process_execute(ls_command)
        client_name = os.path.basename(folders)
        paths = split_the_path(folders)
        working_folder = paths[-2]
        archive_name = working_folder+ "-" +client_name+ "-" + datetime.now().strftime("%Y-%m-%d") + "-"+str(calendar.timegm(time.gmtime()))  + ".tar"
        archive_full_path = tar_location+ "/"+ archive_name
        print "archiving "+folders+ " at "+ archive_full_path
        text_file_name = folders+"/"+archive_name+ ".txt"
        ls_output_file = open(text_file_name, "w")
        ls_output_file.write(ls_output)
        ls_output_file.close()
        tar_command = "tar --absolute-names -zcvf  "+archive_full_path+ " " +folders+ " --remove-files"
        tar_output,tar_error = process_execute(tar_command)

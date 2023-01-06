import os
import re
import sys
import json
import logging
from argparse import ArgumentParser

from paramiko import AutoAddPolicy, SSHClient
from scp import SCPClient

logging.basicConfig(format='"[%(asctime)s][%(levelname).1s] %(message)s',
                    level=logging.INFO)
# logging.getLogger("paramiko").setLevel(logging.WARNING)
logging.getLogger("paramiko").propagate = False



mylogger = logging.getLogger("main")




def MAC_to_ipv6(MAC: str) -> str:
    """Generate the IPv6 address"""

    parts = MAC.split(":")
    # modify parts to match IPv6 value
    parts.insert(3, "ff")
    parts.insert(4, "fe")
    parts[0] = "%x" % (int(parts[0], 16) ^ 2)

    # format output
    ipv6Parts = list()
    for i in range(0, len(parts), 2):
        ipv6Parts.append("".join(parts[i:i+2]))
    ipv6 = "fe80::%s" % (":".join(ipv6Parts))
    return ipv6.lower()

def is_valid_MAC(MAC: str) -> bool:
    """Check the MAC"""

    pattern = r"^([0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}$"
    if re.fullmatch(pattern, MAC):
        return True
    return False

def is_valid_ip(ip: str) -> bool:
    pattern = r"^((25[0-5]|(2[0-4]|1[0-9]|[1-9]|)[0-9])(\.(?!$)|$)){4}"
    if re.fullmatch(pattern, ip):
        return True
    return False

def main():

    # parse args
    parser = ArgumentParser(prog="CYL-SCP",
                            description="CYL-SCP help you get transfer files !",
                            epilog="enjoy !!!\nMark and Ken Love u")

    group = parser.add_mutually_exclusive_group()
    group.add_argument("-P", help="do put (upload)", dest="do_put", action="store_true")
    group.add_argument("-G", help="do get (download)", dest="do_get", action="store_true")

    parser.add_argument("-H", help="host: ip or mac(d0:14:11:b0:0f:12) with interface", dest="host", nargs='+')
    parser.add_argument("-u", help="user name (password)", dest="user_pwd", nargs=2)
    parser.add_argument("-d", help="target directory", dest="target_dir", nargs='?')

    args = parser.parse_args()

    
    config_name = ""
    if args.do_put is True:
        mylogger.info('Upload(put) Mode')
        config_name = "put_config.json"
    elif args.do_get is True:
        mylogger.info('Download(get) Mode')
        config_name = "get_config.json"

    mylogger.info(f'Remote Host:\t{args.host}')

    ## open config file
    try:
        with open(os.path.join(config_name)) as f:
            config = json.load(f)
    except IOError as e:
        print(e)
        return 1

    folders_list = config.get("source_folders")
    files_list = config.get("source_files")

    mylogger.info(f'Folders List:\t{folders_list}')
    mylogger.info(f'Files List:\t{files_list}')

    if folders_list is None and files_list is None:
        mylogger.error('Please add your source list in config json file !')
        mylogger.error('Need at least one key (source_files or source_folders) in json.')
        return 1

    # exit(0)
    host = args.host[0]

    if len(args.host) >=2 and is_valid_MAC(host):
        host = f'{MAC_to_ipv6(host)}%{args.host[1]}'

    target_path = ""
    mode = ""
    if args.target_dir is None:
        if args.do_put is True:
            target_path = "/root"
            mode = "Remote"
        elif args.do_get is True:
            target_path = os.path.join(os.getcwd(), "download", args.host[0].replace(":", ""))
            os.makedirs(target_path, exist_ok=True)
            mode = "Local"

    mylogger.info(f"{mode} Path:\t'{target_path}'")

    port = 22
    username = args.user_pwd[0]
    password = args.user_pwd[1]

    try:
        ssh = SSHClient()
        ssh.set_missing_host_key_policy(AutoAddPolicy())
        ssh.connect(host, port, username, password)

        scp = SCPClient(ssh.get_transport())

        if args.do_put:
            if folders_list is not None and len(folders_list):
                scp.put(folders_list, target_path, recursive=True)
            if files_list is not None and len(files_list):
                scp.put(files_list, target_path)
        elif args.do_get:
            if folders_list is not None and len(folders_list):
                scp.get(folders_list, target_path, recursive=True)
            if files_list is not None and len(files_list):
                scp.get(files_list, target_path)
    except IOError as e:
        print(e)
        return 2
    
    mylogger.info("SCP Program Finished!")

# KKKKKKKKKKKKKKKKKKKK
if __name__ == '__main__':
    mylogger.info("Start SCP Program")
    sys.exit(main())

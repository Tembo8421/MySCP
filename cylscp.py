import json
import logging
import os
import re
import sys
import time
from argparse import ArgumentParser

from paramiko import AutoAddPolicy, SSHClient
from scp import SCPClient

logging.basicConfig(format='[%(asctime)s][%(levelname).1s] %(message)s',
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

def killall_server(ssh,
                   timeout: int = 10):
    start_time = time.time()
    msg = "killall_server timeout"
    while (time.time() - start_time < timeout):
        time.sleep(0.5)
        stdin, stdout, stderr = ssh.exec_command('killall -9 restart_server.sh light_gw_server')
        stdin.close()
        err = stderr.read().decode('utf8')
        if err != "":
            ## comfirm process has been killed.
            if ('restart_server.sh' in err) and ('light_gw_server' in err):
                msg = "light_gw_server process has been killed !"
                print(msg)
                return (True, msg)
            continue

    return False, msg


def main():

    # parse args
    parser = ArgumentParser(prog="CYL-SCP",
                            description="CYL-SCP help you get transfer files !",
                            epilog="enjoy !!!\nMark and Ken Love u")

    group = parser.add_mutually_exclusive_group()
    group.add_argument("-P", help="do put (upload)", dest="do_put", action="store_true")
    group.add_argument("-G", help="do get (download)", dest="do_get", action="store_true")

    parser.add_argument("-H", help="host: ip or mac(d0:14:11:b0:0f:12) with interface", dest="host", nargs='+')
    parser.add_argument("-u", help="username and password", dest="user_pwd", nargs=2)
    parser.add_argument("-c", help="config file", dest="config_file")
    parser.add_argument("-d", help="target directory", dest="target_dir", nargs='?')

    args = parser.parse_args()

    # print(os.getcwd())
    # return 0
    config_name = ""
    if os.path.isfile(args.config_file):
        config_name = args.config_file
    else:
        mylogger.error(f"{args.config_file} need to be a existing json file!")

    if args.do_put is True:
        mylogger.info('Upload(put) Mode')
    elif args.do_get is True:
        mylogger.info('Download(get) Mode')

    mylogger.info(f'Remote Host:\t{args.host}')

    ## open config file
    config_abs = os.path.abspath(config_name)
    try:
        with open(config_abs, 'r', encoding='utf-8') as f:
            config = json.load(f)
    except IOError as e:
        print(e)
        return 1

    config_dir = os.path.dirname(config_abs)
    files_list = []
    if config.get("source_files") is not None:
        for file in config.get("source_files"):
            if args.do_put is True:
                file_abs = file
                if os.path.isabs(file_abs) is False:
                    file_abs = os.path.join(config_dir, file) 
                files_list.append(file_abs)
            else:
                files_list.append(file)

    msg = "\n\t".join(files_list)
    mylogger.info(f'Files List:\n\t{msg}')

    folders_list = []
    if config.get("source_folders") is not None:
        for folder in config.get("source_folders"):
            if args.do_put is True:
                folder_abs = folder
                if os.path.isabs(folder_abs) is False:
                    folder_abs = os.path.join(config_dir, folder)
                folders_list.append(folder_abs)
            else:
                folders_list.append(folder)

    msg = "\n\t".join(folders_list)
    mylogger.info(f'Folders List:\n\t{msg}')

    # exit(0)
    host = args.host[0]

    if len(args.host) >=2 and is_valid_MAC(host):
        host = f'{MAC_to_ipv6(host)}%{args.host[1]}'

    target_path = ""
    mode = ""
    if args.do_put is True:
        if args.target_dir is None:
            target_path = "/"
            mode = "Remote"
        else:
            target_path = args.target_dir
    elif args.do_get is True:
        if args.target_dir is None:
            target_path = os.path.join(config_dir, args.host[0].replace(":", ""))
            mode = "Local"
        else:
            target_path = args.target_dir
            if os.path.isabs(target_path) is False:
                target_path = os.path.join(config_dir, target_path)
        os.makedirs(target_path, exist_ok=True)

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
            # Kill process
            ret, out = killall_server(ssh)
            if not ret:
                return 3

            if folders_list is not None and len(folders_list):
                scp.put(folders_list, target_path, recursive=True)
            if files_list is not None and len(files_list):
                scp.put(files_list, target_path)
        elif args.do_get:
            if folders_list is not None and len(folders_list):
                scp.get(folders_list, target_path, recursive=True)
            if files_list is not None and len(files_list):
                scp.get(files_list, target_path)
    except Exception as e:
        print(e)
        return 2
    
    mylogger.info("SCP Program Finished!")

## Main
if __name__ == '__main__':
    mylogger.info("Start SCP Program")
    sys.exit(main())

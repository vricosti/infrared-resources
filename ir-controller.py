"""
Script Name: ir-controller.py
Purpose: Script to capture remote control key presses and generate a TOML file.
Author: Vincent Richomme
Url: https://raw.githubusercontent.com/vricosti/infrared-resources/main/ir-controller.py
Usage:
    Run the script with -h or --help to see usage options.
"""
import sys
import os
import shutil
import signal
import subprocess
import re
import argparse

def is_process_running(process_name):
    try:
        result = subprocess.run(['pgrep', '-f', process_name], capture_output=True, text=True)
        return bool(result.stdout.strip())
    except:
        return False
    
def is_binary_installed(binary_name):
    return shutil.which(binary_name) is not None

def exec_get_output(args):
    result = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, timeout=10)
    return result.stdout

def extract_lirc_section(output):
    # Regular expression to match sections from "Found /sys/..." till either the next "Found /sys/..." or end of string
    sections = re.findall(r"Found /sys/class/rc/.*?(?=Found /sys/class/rc/|$)", output, re.DOTALL)

    # Return the section that contains 'lirc'
    for section in sections:
        if 'lirc' in section:
            return section
    return None

def is_lirc_protocol_enabled():
    try:
        output = exec_get_output(['ir-keytable'])

        # Extract the section containing 'lirc'
        lirc_section = extract_lirc_section(output)
        if not lirc_section:
            print("LIRC section not found in ir-keytable output.")
            return False
         
        print(lirc_section)
        
        # Extract "Enabled kernel protocols" line from the lirc section
        match = re.search(r"Enabled kernel protocols:\s*([^\n]+)", lirc_section)

        if match:
            protocols = match.group(1).strip().split()
            if 'lirc' not in protocols or len(protocols) > 1:
                print("****")
                print(f"Enabled kernel protocols have: {protocols}.")
                print("Ensure only 'lirc' is enabled because ir-keytable engine is buggy and we want to receive raw data to decode ourself.")
                print("Please enter the following cmd then restart this script: sudo ir-keytable -p lirc")
                print("****")
                return False
        else:
            print("Unable to extract 'Enabled kernel protocols' from LIRC section.")
            return False

        return True
    except Exception as e:
        print(f"Error checking if LIRC protocol is enabled: {e}")
        return False


def parse_arguments():
    parser = argparse.ArgumentParser(description='Script to capture remote control key presses and generate a TOML file.')
    parser.add_argument('-d', '--device', default='/dev/lirc1', help='device to control. Defaults to /dev/lirc1 if not specified.')
    return parser.parse_args()

def check_env():
    # check that ir-keytable is installed
    for binary in ['ir-keytable', 'ir-ctl']:
        if not is_binary_installed(binary):
            print(f"{binary} is not available. Please install ir-keytable (ex: sudo apt install ir-keytable on debian based distribution).")
            return False
    
    # check that lircd is not running
    if is_process_running('lircd'):
        print("lircd process is running. Please stop it and try again (ex: sudo systemctl stop lircd).")
        return False
        
    # check that ir-keytable output has a section lirc and extract information to check if
    # Enabled kernel protocols has only lirc.
    if not is_lirc_protocol_enabled():
        return False
    
    return True


# ir-ctl -v -d /dev/lirc-rx -r
def main():
    try:
        args = parse_arguments()

        if not check_env():
            return
        



    except KeyboardInterrupt:
        print("\n\nScript interrupted by user. Exiting gracefully.")
        sys.exit(0)


if __name__ == "__main__":
    main()

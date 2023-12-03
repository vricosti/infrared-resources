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

supported_protocols = []
enabled_protocols = []

SUPPORTED_KERNEL_PROTOCOLS = "Supported kernel protocols"
ENABLED_KERNEL_PROTOCOLS = "Enabled kernel protocols"


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

def extract_key_value_pairs(ir_output):
    # Split the output into lines for easier processing
    lines = ir_output.strip().split('\n')
    
    # Pattern to match keys and values, including those with colons in the value
    pattern = re.compile(r'(\w[\w\s]*(?=\s*:))\s*:\s*([^,]+)')
    
    # Dictionary to hold the key-value pairs
    result = {}
    
    # Process each line
    for line in lines:
        # Find all matches in the current line
        matches = pattern.findall(line)
        
        # Add each key-value pair to the dictionary
        for key, value in matches:
            # Clean up and standardize the key and value
            clean_key = key.strip()
            clean_value = value.strip().rstrip(',')
            # Add to dictionary
            result[clean_key] = clean_value
            
    return result


def extract_lirc_values(output):
    key_values = {}

    # Regular expression to match sections from "Found ... with:" till either the next "Found ... with:" or end of string
    sections = re.findall(r"Found .*? with:.*?(?=Found .*? with:|$)", output, re.DOTALL)

    # Return the *first* section that contains 'lirc'
    for section in sections:
        # Check if 'lirc' is in section and then extract key-value pairs
        if 'lirc' in section:
            # Extract the sysdev path and add it to key_values
            sysdev_path_match = re.search(r"Found (.*?) with:", section)
            if sysdev_path_match:
                sysdev_path = sysdev_path_match.group(1).strip()
                key_values['__sysdev__'] = sysdev_path
                key_values.update(extract_key_value_pairs(section))
                break
    return key_values

def match_and_extract_as_array(text_to_match, lirc_section):
    matched = []
    match = re.search(r"{}:\s*([^\n]+)".format(text_to_match), lirc_section)
    if match:
        matched = match.group(1).strip().split()
    else:
        print(f"Unable to extract {text_to_match} from LIRC section.")
    return matched
    
    
def is_lirc_protocol_enabled():
    try:
        output = exec_get_output(['ir-keytable'])

        # Extract the section containing 'lirc'
        lirc_values = extract_lirc_values(output)
        if not lirc_values:
            print("LIRC section not found in ir-keytable output.")
            return False
         
        
        # Extract "Enabled kernel protocols" line from the lirc section
        enabled_protocols = match_and_extract_as_array("Enabled kernel protocols", lirc_section)

        match = re.search(r"Enabled kernel protocols:\s*([^\n]+)", lirc_section)
        if match:
            enabled_protocols = match.group(1).strip().split()
            if 'lirc' not in enabled_protocols or len(enabled_protocols) > 1:
                print("****")
                print(f"Enabled kernel protocols have: {enabled_protocols}.")
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
            print(f"{binary} is not available. Please install {binary} (ex: sudo apt install v4l-utils on debian based distribution).")
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

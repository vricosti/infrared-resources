"""
Script Name: ir-keytable-record.py
Purpose: Script to capture remote control key presses and generate a TOML file.
Author: Vince Ricosti
Url: https://raw.githubusercontent.com/vricosti/infrared-resources/main/ir-keytable-record.py
Usage:
    Run the script with -h or --help to see usage options.
"""
import os
import subprocess
import re
import time
import signal
import argparse

def get_ir_keytable_output(sysdev):
    cmd = ["stdbuf", "-oL", "ir-keytable", "-s", sysdev, "-t"]
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1, universal_newlines=True)

    lines = []
    for line in iter(process.stdout.readline, ''):
        lines.append(line)
        if "lirc protocol" in line:
            break

    process.send_signal(signal.SIGINT)
    process.communicate()

    return ''.join(lines)

def extract_protocol_and_scancode(output):
    # Extract lines containing "lirc protocol"
    match = re.search(r"lirc protocol\(([^)]+)\): scancode = (0x[\da-fA-F]+)", output)
    if match:
        protocol, scancode = match.groups()
        return protocol, scancode
    return None, None

def parse_arguments():
    parser = argparse.ArgumentParser(description='Script to capture remote control key presses and generate a TOML file.')
    parser.add_argument('-s', '--sysdev', default='rc0', help='RC device to control. Defaults to rc0 if not specified.')
    return parser.parse_args()

def main():
    args = parse_arguments()
    sysdev = args.sysdev

    filename = input("Please enter the file name: ").strip()
    filename_no_ext, ext = os.path.splitext(filename)
    if not ext:
        filename = f"{filename}.toml"

    keys_dict = {}
    global_protocol = None

    while True:
        key_name = input("Enter the key name (in upper case) or a space to stop: ").strip()
        if key_name == '':
            break

        #print("Please press the button on your remote for key:", key_name)
        output = get_ir_keytable_output(sysdev)
        protocol, scancode = extract_protocol_and_scancode(output)
        if protocol and scancode:
            print(f'{scancode} = "{key_name}" #protocol ="{protocol}"')
            keys_dict[key_name] = scancode
            if not global_protocol:
                global_protocol = protocol
                if global_protocol == 'rc5x_20':
                    global_protocol = 'rc5'

    with open(filename, 'w') as f:
        f.write("[[protocols]]\n")
        f.write(f'name = "{filename_no_ext}"\n')
        f.write(f'protocol = "{global_protocol}"\n')
        f.write(f'variant = "{global_protocol}"\n')
        f.write("[protocols.scancodes]\n")
        for key_name, scancode in keys_dict.items():
            f.write(f'{scancode} = "{key_name}"\n')

    print(f"File '{filename}' has been written.")

if __name__ == "__main__":
    main()


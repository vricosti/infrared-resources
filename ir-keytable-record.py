"""
Script Name: ir-keytable-record.py
Purpose: Script to capture remote control key presses and generate a TOML file.
Author: Vince Ricosti
Url: https://raw.githubusercontent.com/vricosti/infrared-resources/main/ir-keytable-record.py
Usage:
    Run the script with -h or --help to see usage options.
"""
import sys
import os
import signal
import subprocess
import re
import argparse
from collections import defaultdict


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
    match = re.search(r"lirc protocol\(([^)]+)\): scancode = (0x[\da-fA-F]+)", output)
    if match:
        return match.groups()
    return None, None


def parse_arguments():
    parser = argparse.ArgumentParser(description='Script to capture remote control key presses and generate a TOML file.')
    parser.add_argument('-s', '--sysdev', default='rc0', help='RC device to control. Defaults to rc0 if not specified.')
    return parser.parse_args()


def main():
    try:
        args = parse_arguments()
        sysdev = args.sysdev

        filename = input("Please enter the file name (without extension): ").strip() + '.toml'

        # Dict to store protocols and their associated keys and scancodes
        protocols_dict = defaultdict(lambda: {"name": "", "protocol": "", "variant": "", "scancodes": {}})

        while True:
            key_name = input("Enter the key name (in upper case) or just press ENTER to stop: ").strip()
            if key_name == '':
                break

            output = get_ir_keytable_output(sysdev)
            protocol, scancode = extract_protocol_and_scancode(output)
            if protocol and scancode:
                print(f'Detected key {key_name} with scancode {scancode} for protocol {protocol}')
                if not protocols_dict[protocol]['name']:
                    protocols_dict[protocol].update({"name": protocol, "protocol": protocol, "variant": protocol})
                protocols_dict[protocol]['scancodes'][scancode] = key_name

        with open(filename, 'w') as f:
            for protocol, data in protocols_dict.items():
                f.write(f"[[protocols]]\n")
                f.write(f'name = "{data["name"]}"\n')
                f.write(f'protocol = "{data["protocol"]}"\n')
                f.write(f'variant = "{data["variant"]}"\n')
                f.write("[protocols.scancodes]\n")
                for scancode, key_name in data['scancodes'].items():
                    f.write(f'{scancode} = "{key_name}"\n')
                f.write("\n")

        print(f"File '{filename}' has been written.")
    except KeyboardInterrupt:
        print("\n\nScript interrupted by user. Exiting gracefully.")
        sys.exit(0)


if __name__ == "__main__":
    main()


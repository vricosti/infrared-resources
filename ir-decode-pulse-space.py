import argparse

def normalize_to_sony_protocol(data):
    # Define tolerances and target values
    tolerance = 80
    header_mark = 2400
    header_space = -600
    mark_0_or_1 = 600
    space_0 = -600
    space_1 = -1200
    mark_space_2 = 1200

    # Check if the first two values match the header
    if abs(data[0] - header_mark) <= tolerance and abs(data[1] - header_space) <= tolerance:
        # Normalize the subsequent values
        for i in range(2, len(data)):
            if abs(data[i] - mark_0_or_1) <= tolerance:
                data[i] = mark_0_or_1
            elif abs(data[i] - space_0) <= tolerance:
                data[i] = space_0
            elif abs(data[i] - space_1) <= tolerance:
                data[i] = space_1
            elif abs(data[i] - mark_space_2) <= tolerance:
                data[i] = mark_space_2

    return data

def main():
    parser = argparse.ArgumentParser(description='Decode IR data using Sony protocol')
    parser.add_argument('-f', '--file', required=True, help='File containing IR data')

    args = parser.parse_args()

    # Read data from the specified file
    with open(args.file, 'r') as file:
        content = file.readline().strip()

    # Check if '# timeout' exists
    timeout_str = ""
    if "# timeout" in content:
        data_str, timeout_str = content.split("# timeout", 1)
        timeout_str = "# timeout" + timeout_str
    else:
        data_str = content

    # Convert main data to integers
    data = [int(val) for val in data_str.split() if val.replace('+', '').replace('-', '').isdigit()]

    normalized_data = normalize_to_sony_protocol(data)

    # Convert the normalized data back to string format
    normalized_str = ' '.join(['+' + str(val) if val > 0 else str(val) for val in normalized_data])
    print(normalized_str, timeout_str.strip())

if __name__ == "__main__":
    main()


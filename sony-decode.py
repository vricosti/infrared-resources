import re
import sys

def decode_ir_signal(ir_codes):
    # Remove the text after '#' if any
    ir_codes = re.sub(r'#.*', '', ir_codes).strip()

    # Split the IR codes into a list
    codes_list = ir_codes.split()
    
    decoded_signals = []
    current_signal = []
    i = 0
    
    while i < len(codes_list):
        value = int(codes_list[i][1:])
        
        if value == 2400:  # Start of a new signal
            if current_signal:
                prefix = "sony12:" if len(current_signal) == 12 else "sony15:"
                decoded_signals.append(f"{prefix} {''.join(current_signal)}")
                current_signal = []
            i += 2  # Skip the start signal and the following -600 space
        elif value == 1200:  # Burst corresponding to '1'
            current_signal.append('1')
            i += 2  # Skip the burst and the following -600 space
        elif value == 600:  # Burst corresponding to '0'
            current_signal.append('0')
            i += 2  # Skip the burst and the following -600 space
        else:  # Skip any unexpected values
            i += 1

    # Append the last decoded signal
    if current_signal:
        prefix = "sony12:" if len(current_signal) == 12 else "sony15:"
        decoded_signals.append(f"{prefix} {''.join(current_signal)}")

    return '\n'.join(decoded_signals)


#sony12: 010010010000


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 decode_ir.py '<IR_CODES_STRING>'")
        sys.exit(1)

    input_ir_codes = sys.argv[1]
    decoded_signal = decode_ir_signal(input_ir_codes)
    print(decoded_signal)

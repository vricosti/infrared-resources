import re
import sys

def normalize_ir_codes(ir_codes):
    # Remove the text after '#' if any
    ir_codes = re.sub(r'#.*', '', ir_codes).strip()

    # Split the IR codes into a list
    codes_list = ir_codes.split()

    # Convert the string values to integers and normalize to around 600
    normalized_codes = []
    for code in codes_list:
        sign = 1 if code[0] == '+' else -1
        value = int(code[1:])
        normalized_value = round(value / 600) * 600
        normalized_codes.append(f"{'+' if sign == 1 else '-'}{normalized_value}")

    # Join the normalized values back into a string
    normalized_ir_codes = ' '.join(normalized_codes)
    return normalized_ir_codes

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 normalize.py '<IR_CODES_STRING>'")
        sys.exit(1)

    input_ir_codes = sys.argv[1]
    normalized_ir_codes = normalize_ir_codes(input_ir_codes)
    print(normalized_ir_codes)

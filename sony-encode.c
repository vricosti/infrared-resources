#include <stdio.h>
#include <string.h>

#define LIRCBUF_SIZE 1024
#define IR_DEFAULT_TIMEOUT 125000
#define UNSET UINT32_MAX

enum rc_proto
{
    RC_PROTO_UNKNOWN = 0,
    RC_PROTO_OTHER = 1,
    RC_PROTO_RC5 = 2,
    RC_PROTO_RC5X_20 = 3,
    RC_PROTO_RC5_SZ = 4,
    RC_PROTO_JVC = 5,
    RC_PROTO_SONY12 = 6,
    RC_PROTO_SONY15 = 7,
    RC_PROTO_SONY20 = 8,
    RC_PROTO_NEC = 9,
    RC_PROTO_NECX = 10,
    RC_PROTO_NEC32 = 11,
    RC_PROTO_SANYO = 12,
    RC_PROTO_MCIR2_KBD = 13,
    RC_PROTO_MCIR2_MSE = 14,
    RC_PROTO_RC6_0 = 15,
    RC_PROTO_RC6_6A_20 = 16,
    RC_PROTO_RC6_6A_24 = 17,
    RC_PROTO_RC6_6A_32 = 18,
    RC_PROTO_RC6_MCE = 19,
    RC_PROTO_SHARP = 20,
    RC_PROTO_XMP = 21,
    RC_PROTO_CEC = 22,
    RC_PROTO_IMON = 23,
    RC_PROTO_RCMM12 = 24,
    RC_PROTO_RCMM24 = 25,
    RC_PROTO_RCMM32 = 26,
    RC_PROTO_XBOX_DVD = 27,
    RC_PROTO_MAX = RC_PROTO_XBOX_DVD,
};

#define NS_TO_US(x) (((x) + 500) / 1000)

static const int sony_unit = 600000;

static void sony_add_bits(unsigned *buf, int *n, int bits, int count)
{
    int i;
    for (i = 0; i < count; i++)
    {
        if (bits & (1 << i))
            buf[(*n)++] = NS_TO_US(sony_unit * 2);
        else
            buf[(*n)++] = NS_TO_US(sony_unit);

        buf[(*n)++] = NS_TO_US(sony_unit);
    }
}

static int sony_encode(enum rc_proto proto, unsigned scancode, unsigned *buf)
{
    int n = 0;

    buf[n++] = NS_TO_US(sony_unit * 4);
    buf[n++] = NS_TO_US(sony_unit);

    switch (proto)
    {
    case RC_PROTO_SONY12:
        sony_add_bits(buf, &n, scancode, 7);
        sony_add_bits(buf, &n, scancode >> 16, 5);
        break;
    case RC_PROTO_SONY15:
        sony_add_bits(buf, &n, scancode, 7);
        sony_add_bits(buf, &n, scancode >> 16, 8);
        break;
    case RC_PROTO_SONY20:
        sony_add_bits(buf, &n, scancode, 7);
        sony_add_bits(buf, &n, scancode >> 16, 5);
        sony_add_bits(buf, &n, scancode >> 8, 8);
        break;
    default:
        return 0;
    }

    /* ignore last space */
    return n - 1;
}

static unsigned int decode_sirc(unsigned int *buf, int n, enum rc_proto proto) {
    unsigned int scancode = 0;
    unsigned int command_bits = 0, device_bits = 0;
    int bit_pos = 0;

    // Skip the start sequence
    for (int i = 2; i < n; i += 2) {
        if (buf[i] > 1000) {  // Threshold for '1'
            if (bit_pos < 7) {
                command_bits |= (1 << bit_pos);  // First 7 bits (command)
            } else {
                device_bits |= (1 << (bit_pos - 7));  // Subsequent bits (device)
            }
        }
        bit_pos++;
    }

    scancode = command_bits | (device_bits << 16);

    return scancode;
}

static unsigned int decode_binary_sirc(const char *binary, enum rc_proto proto) {

    int bit_length = strlen(binary);
    unsigned int scancode = 0;
    unsigned int command_bits = 0, device_bits = 0;
    //int bit_pos = 0;


    for (int i = 0; i < bit_length; i++) {
        if (binary[i] == '1') {
            if (i < 7) {
                command_bits |= (1 << i);  // First 7 bits (command)
            } else {
                device_bits |= (1 << (i - 7));  // Subsequent bits (device)
            }
         }
         //bit_pos++;
     }

    scancode = command_bits | (device_bits << 16);

    return scancode;
}


static void display_binary(int number)
{
    // Define the size of an integer in bits
    int bits = sizeof(int) * 8;

    // Iterate over each bit position
    for (int i = bits - 1; i >= 0; i--)
    {
        // Print the bit at the current position
        printf("%d", (number >> i) & 1);

        // Optional: Print a space every 4 bits for readability
        if (i % 4 == 0)
        {
            printf(" ");
        }
    }

    // Print a newline at the end
    printf("\n");
}

// void display_binary(int number) {
//     // Define the size of an integer in bits
//     int bits = sizeof(int) * 8;

//     // Iterate over each bit position
//     for (int i = 0; i < bits; i++) {
//         // Print the bit at the current position
//         printf("%d", (number >> i) & 1);

//         // Optional: Print a space every 4 bits for readability
//         if ((i + 1) % 4 == 0) {
//             printf(" ");
//         }
//     }

//     // Print a newline at the end
//     printf("\n");
// }

int main()
{
    unsigned buf[LIRCBUF_SIZE];
    int scancode = 0x10012;

    if (0)
    {
        //+2400 -600 +600 -600 +1200 -600 +600 -600 +600 -600 +1200 -600 +600 -600 +600 -600 +1200 => 01001001...
        // 010010010000
        display_binary(scancode); ////0000 0000 0000 0001 0000 0000 0001 0010
        sony_encode(RC_PROTO_SONY12, scancode, &buf);
    }
    else
    {

        unsigned int buf[LIRCBUF_SIZE];
        unsigned int pulse_widths[] = {
            2400, 600, 600, 600, 1200, 600, 600, 600, 600, 600, 1200, 600, 600, 600, 600, 600, 1200,
            600, 600, 600, 600, 600, 600, 600, 600, 600, 26400, 2400, 600, 600, 600, 1200, 600, 600,
            600, 600, 600, 1200, 600, 600, 600, 600, 600, 1200, 600, 600, 600, 600, 600, 600, 600,
            600, 26400, 2400, 600, 600, 600, 1200, 600, 600, 600, 600, 600, 1200, 600, 600, 600, 600,
            600, 1200, 600, 600, 600, 600, 600, 600, 600};
        int n = sizeof(pulse_widths) / sizeof(pulse_widths[0]);

        int start_index = 0;

        while (start_index < n)
        {
            // Find the next start pulse
            while (start_index < n && !(pulse_widths[start_index] == 2400 && pulse_widths[start_index + 1] == 600))
            {
                start_index++;
            }

            if (start_index >= n)
                break; // No more start pulses found

            // Decode the frame starting at this pulse
            unsigned int scancode = decode_sirc(pulse_widths + start_index, 26, RC_PROTO_SONY12); // 26 pulses for 12-bit SIRC
            printf("Decoded Scancode: 0x%X\n", scancode);
            display_binary(scancode);

            // Move to the next frame (skip over the current frame and the long gap)
            start_index += 26 + 1;
        }

        const char *binary_string = "010010010000"; // Example binary string
        //const char *binary_string = "000010010010"; // Example binary string
        unsigned int scancode = decode_binary_sirc(binary_string, RC_PROTO_SONY12);
        printf("Decoded Scancode: 0x%X\n", scancode);
    }




    return 0;
}
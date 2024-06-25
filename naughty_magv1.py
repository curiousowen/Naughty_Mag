import argparse
from wave import open as open_wave
from struct import pack
from operator import xor

# Constants
BITS_TRACK_1 = 7
BITS_TRACK_2_3 = 5
BASE_TRACK_1 = 32
BASE_TRACK_2_3 = 48
MAX_TRACK_1 = 63
MAX_TRACK_2_3 = 15

# Globals
bits = BITS_TRACK_1
base = BASE_TRACK_1
max_value = MAX_TRACK_1

def parse_arguments():
    parser = argparse.ArgumentParser(description='Encode or decode magnetic stripe data.')
    
    parser.add_argument('-t', '--track', type=int, choices=[1, 2, 3], default=1,
                        help='Specify track number (default: 1)')
    parser.add_argument('-c', '--card_data', type=str,
                        help='Data for the track')
    parser.add_argument('-b', '--card_data2', type=str,
                        help='Data for the second track')
    parser.add_argument('-z', '--leading_zeros', type=int, default=25,
                        help='Number of leading zeros (default: 25)')
    parser.add_argument('-s', '--samples_per_bit', type=int, default=15,
                        help='Samples per bit, recommended [5-45] (default: 15)')
    parser.add_argument('-f', '--file_name', type=str,
                        help='WAV file name (if not specified, only shows binary encode)')
    parser.add_argument('-d', '--decode_data', type=str,
                        help='MagStripe Binary to decode')
    parser.add_argument('-r', '--reverse_magstripe', type=int, choices=[0, 1], default=0,
                        help='Reverse MagStripe (default: 0)')
    
    return parser.parse_args()

def set_track_parameters(track_number):
    global bits, base, max_value
    if track_number in [2, 3]:
        bits = BITS_TRACK_2_3
        base = BASE_TRACK_2_3
        max_value = MAX_TRACK_2_3
    else:
        bits = BITS_TRACK_1
        base = BASE_TRACK_1
        max_value = MAX_TRACK_1

def decode_magstripe(data):
    start_decode = data.find("1010001")
    if start_decode < 0:
        raise ValueError("No start sentinel found!")

    end_sentinel = data.find("1111100")
    while (end_sentinel - start_decode) % 7:
        newpos = data[end_sentinel + 1:].find("1111100")
        if newpos >= 0:
            end_sentinel += newpos + 1
        else:
            raise ValueError("No end sentinel found!")

    actual_lrc = end_sentinel + 7
    rolling_lrc = [0] * 7
    decoded_string = ''

    while start_decode <= end_sentinel:
        asciichr = 32
        parity = int(data[start_decode + 6])

        for x in range(6):
            asciichr += int(data[start_decode + x]) << x
            parity += int(data[start_decode + x])
            rolling_lrc[x] = xor(rolling_lrc[x], int(data[start_decode + x]))

        if not parity % 2:
            raise ValueError("Parity error!")

        decoded_string += chr(asciichr)
        start_decode += 7

    parity = 1
    for x in range(6):
        parity += rolling_lrc[x]

    rolling_lrc[6] = parity % 2
    for x in range(7):
        if rolling_lrc[x] != int(data[actual_lrc + x]):
            raise ValueError("LRC/CRC check failed!")

    print("Decoded result:")
    print(decoded_string)

def encode_magstripe(data, padding, frequency):
    set_track_parameters(1 if data.startswith('%') else 2)
    lrc = [0] * bits
    output = '0' * padding

    for char in data:
        raw = ord(char) - base
        if raw < 0 or raw > max_value:
            raise ValueError(f'Illegal character: {chr(raw + base)}')

        parity = 1
        for y in range(bits - 1):
            output += str((raw >> y) & 1)
            parity += (raw >> y) & 1
            lrc[y] = xor(lrc[y], (raw >> y) & 1)

        output += chr((parity % 2) + ord('0'))

    parity = 1
    for x in range(bits - 1):
        output += chr(lrc[x] + ord('0'))
        parity += lrc[x]

    output += chr((parity % 2) + ord('0'))
    output += '0' * padding
    return output

def generate_wav(data, file_name, frequency, reverse_magstripe, card2_data):
    if not file_name:
        return

    print(f"Creating wav file: {file_name}")
    with open_wave(file_name, "w") as newtrack:
        params = (1, 2, 22050, 0, 'NONE', 'not compressed')
        newtrack.setparams(params)
        peak = 32767

        for _ in range(2):
            n = 0
            while n < len(data):
                writedata = peak
                if data[n] == '1':
                    for _ in range(2):
                        writedata = -writedata
                        for _ in range(frequency // 4):
                            newtrack.writeframes(pack("h", writedata))
                elif data[n] == '0':
                    writedata = -writedata
                    for _ in range(frequency // 2):
                        newtrack.writeframes(pack("h", writedata))
                n += 1

            if card2_data and card2_data.startswith(';'):
                data = encode_magstripe(card2_data, 0, frequency)
            elif not reverse_magstripe or not data.startswith(';'):
                break
            data = data[::-1]

        print("Done")

def main():
    args = parse_arguments()

    if args.decode_data:
        decode_magstripe(args.decode_data)
    else:
        if not args.card_data:
            print("No card data provided. Use -c or --card_data to specify the card data.")
            return

        set_track_parameters(args.track)
        encoded_data = encode_magstripe(args.card_data, args.leading_zeros, args.samples_per_bit)
        generate_wav(encoded_data, args.file_name, args.samples_per_bit, args.reverse_magstripe, args.card_data2)

if __name__ == '__main__':
    main()

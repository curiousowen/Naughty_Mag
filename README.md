# Naughty_Mag
Simple Tool to try get some info from insecure mag card mechanisms

This tool allows you to encode and decode magnetic stripe data. It supports working with different track numbers, specifying various encoding parameters, and generating WAV files for the encoded data.
Features

    Encode magnetic stripe data for tracks 1, 2, and 3.
    Decode binary magnetic stripe data.
    Customize encoding parameters such as leading zeros, samples per bit, and reverse encoding.
    Generate WAV files with the encoded data.

Requirements

    Python 3.x

Installation

No special installation is required. Simply download the script and run it with Python.
Usage
Command-Line Options

The script uses command-line arguments to specify the encoding and decoding parameters. Here are the available options:

    -t, --track: Specify the track number (1, 2, or 3). Default is 1.
    -c, --card_data: Data for the track.
    -b, --card_data2: Data for the second track.
    -z, --leading_zeros: Number of leading zeros. Default is 25.
    -s, --samples_per_bit: Samples per bit. Recommended range is 5-45. Default is 15.
    -f, --file_name: WAV file name. If not specified, only binary encoding will be shown.
    -d, --decode_data: MagStripe binary data to decode.
    -r, --reverse_magstripe: Reverse MagStripe (0 or 1). Default is 0.

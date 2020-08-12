#!/usr/bin/env python3

import hcl
import json
import argparse
"""
Usage : python3 tf-to-json.py --input configrule.tf --output config-out.json 

"""


def tf_to_json(input_file, output_file):

    with open('configrule.tf', 'r') as fp:
        json_out = hcl.load(fp)

    with open('config-out.json', 'w') as outfile:
        json.dump(json_out, outfile, indent=4)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='converting tf file to json file')
    parser.add_argument('--input',
                        help='give the input tf file to change',
                        required=True)
    parser.add_argument('--output',
                        help='give the output json file to create',
                        required=True)
    args = parser.parse_args()

    tf_to_json(args.input, args.output)

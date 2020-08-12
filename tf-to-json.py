import hcl
import json

with open('configrule.tf', 'r') as fp:
    json_out = obj = hcl.load(fp)

with open('config-out.json', 'w') as outfile:
    json.dump(json_out, outfile, indent=4)
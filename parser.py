import json
import sys

if len(sys.argv) != 2:
    print("Usage: python script.py <input_file_path>")
    sys.exit(1)

input_file_path = sys.argv[1]

try:
    with open(input_file_path, 'r') as f:
        parsedInfo = json.load(f)

    violations = parsedInfo["files"][0]['violations']
    for i in violations:
        k = i.pop('priority')
        if k == 1:
            i['priority'] = 'ERROR'
        elif k == 2 or k == 3:
            i['priority'] = 'WARNING'
        else:
            i['priority'] = 'INFO'

    result_list = []
    result_dict = {"violations": result_list}
    for k in parsedInfo["files"]:
        for j in k['violations']:
            dictionary = {
                'file': k['filename'],
                'name': j['rule'],
                'priority': j['priority'],
                'message': j['description'],
                'line': j['beginline'],
                'column': j['begincolumn'],
                'severity': j['priority']
            }
            result_dict['violations'].append(dictionary)
    print ('test')
    with open('reportfile.json', 'w') as outfile:
        json.dump(result_dict, outfile)

except FileNotFoundError:
    print(f"Error: File not found at '{input_file_path}'")
except json.JSONDecodeError:
    print("Error: Invalid JSON format in the input file")

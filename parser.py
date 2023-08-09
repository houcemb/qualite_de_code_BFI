import json

f = open('D:\\test\\test.json','r')
parsedInfo= json.load(f)


violations = parsedInfo["files"][0]['violations']
for i in violations :
    
    k= i.pop('priority')
    if k == 1:
        i['priority'] = 'ERROR'
    elif k == 2| k == 3:
        i['priority'] = 'WARNING'
    else:
        i['priority'] = 'INFO'

with open('reportfile.json','w') as outfile:
    json.dump(violations, outfile)
outfile.close( )
f.close( )
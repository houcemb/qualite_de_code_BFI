import argparse
from functools import cache
import html
import subprocess
import json

import os
import sys
import xml.etree.ElementTree as ET



## enumeration
ERROR = "ERROR" 
WARNING = "WARNING"
INFO = "INFO" 
def error_handler_with_exit(error):
    print("Error:", error)
    sys.exit(1)
def error_handler_without_exit(error):
    print("Error:", error)
    
def run_tool (command):
    try:
        result = subprocess.run(command,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                text=True,
                                check=True)
        return result.stdout
    except subprocess.SubprocessError as e:
        error_handler_with_exit(e)

def run_pmd(fileDirectory,ruleset):
    pmd_command = ['pmd', 'check',"-f","json"]+ fileDirectory+[ '-R', ruleset,"--no-fail-on-violation"]
    #!!!!!!!!!!!!problem if runtool prints error and returns nothing
    
    return json.loads(run_tool(pmd_command))
   

def run_semgrep(rules,code):
    semgrep_command = ["semgrep","--config",rules,"--junit-xml"]+code+["--quiet"]
    return (run_tool(semgrep_command))

def severity_normalizer(x):
    match x:
        case 1:
            severity = ERROR
        case 2 | 3:
            severity = WARNING
        case 4 | 5:
            severity = INFO
    # which default value to use ?????????????
        case _:
            severity = "not defined severity"
    return severity 
def file_name_normalizer(fileDirectory,fileName):
    for file in fileDirectory:
        if os.path.basename(file) == os.path.basename(fileName):
            return file
# dont use dict as a variable name
def pmd_parser(non_parsed_report,fileDirectory ):
    violations=[{
                'file': file_name_normalizer(fileDirectory,dict['filename']),
                'name': violation['rule'],
                'priority': violation['priority'],
                'message': violation['description'],
                'line': violation['beginline'],
                'severity': severity_normalizer(violation['priority'])
            } for dict in non_parsed_report["files"] for violation in dict['violations']]


    return {"violations":violations}
#this is a function that use find to verify the structure of xml file 
def search_tag(parent,child):
    try:
        return parent.find(child)
    except AttributeError | TypeError as e:
        error_handler_without_exit(e)
    
#this function that use findall
def search_tags(parent,child):
    try:
        return parent.findall(child)
    except AttributeError | TypeError as e:
        error_handler_without_exit(e)


def semgrep_parser(junit_output):
        root = ET.fromstring(junit_output)
        models=search_tags(root,".//testcase")
        violations=[{"name":i.get('name'),
                        "file":i.get('file'),
                        "line":i.get('line'),
                        "severity":f.get('type'),
                        "message":f.get('message')
                } for i in models for f in [search_tag(i, "failure")]
                                        if f is not None ]


        return {"violations":violations}

def result_dic(violations_list):
    warning_count = 0
    info_count = 0
    error_count = 0
   
    for violations in violations_list:
        for violation in violations["violations"]:
            severity = violation.get("severity")
            if severity == WARNING:
                warning_count += 1
            elif severity == INFO:
                info_count += 1
            elif severity == ERROR:
                error_count += 1
    return {"WARNING": warning_count, "INFO": info_count, "ERROR": error_count}

def score_calculator(dic):
    dic_score={}
    dic_score ["score"] = 10
    dic_score["WARNING"] = dic["WARNING"]
    dic_score["INFO"] = dic["INFO"]
    dic_score["ERROR"] = dic["ERROR"]
    if dic["ERROR"] > 0:
        dic_score ["score"] = 0
        dic_score ["result"] = False 
    else :

        s=10 - dic["WARNING"]- dic["INFO"]*0.5
        dic["score"] = s if s > 0 else 0
        dic_score ["result"] = dic_score ["score"]>=5
        
    return dic_score
@cache
def read_lines_from_file(filename):
    try:
       
        with open(filename) as file:
            return file.readlines()  
    except IOError as e:
       error_handler_without_exit(e)
       return []



def extract_code(filename, linenumber):   
    
    lines = read_lines_from_file(filename)
    line = int(linenumber)
    beginningline = max(0,line-3)
    endingline = min(len(lines),line+2)
   
    return {"before": "".join(lines[beginningline:line-1]), "line": lines[line-1], "after": "".join(lines[line:endingline])}
   
      
def html_generator(parsed_report_pmd,parsed_report_semgrep,score_dict,path,fileDirectory):
    
    html_template = """
<!DOCTYPE html>
<html>
<head>
<link rel="stylesheet" href="./pico/css/pico.min.css">

    <title>Score Report</title>
    <link href="prism/prism.css" rel="stylesheet" />

</head>
<body>
    <h1 style="padding: 20px;" >Score Report</h1>
     <ul style="padding: 40px;">
        <li>Result : {passed}</li>
        <li>Score : {score}</li>
        <li>WARNING count : {warning_count}</li>
        <li>INFO count : {info_count}</li>
        <li>ERROR count : {error_count}</li>
    </ul>
    <h2 style="padding: 30px;">Violations Details</h2>
    <thead>
    <table border="5">
    <thead>
        <tr>
            <th>File</th>
            <th>Rule Name</th>
            <th>Message</th>
            <th>Line in Code</th>
            <th>Severity</th>
            <th>error code </th>
            
        </tr>
    </thead>
    <tbody>
        {parsed_report_loop}
    </tbody>
    </table>
    
    <script src="prism.js"></script>

</body>
</html>
"""

# Generate content for PMD violations

    parsed_report_loop = ""
    for violation in parsed_report_pmd['violations'] + parsed_report_semgrep['violations']:
        extracted_code= extract_code(violation['file'],violation['line'])
        parsed_report_loop += f"""
    <tr>
        <td>{violation['file']}</td>
        <td>{violation['name']}</td>
        <td>{violation['message']}</td>
        <td>{violation['line']}</td>
        <td>{violation['severity']}</td>   
        <td><PRE> {html.escape("".join(extracted_code["before"]))}<code class="language-java">{html.escape(extracted_code["line"])}</code>{html.escape(extracted_code["after"])}</PRE></td>

    </tr>
"""


            
        
# Format the HTML template with dynamic data and generated loops
    rendered_html = html_template.format(
    warning_count=score_dict["WARNING"],
    info_count= score_dict["INFO"] ,
    error_count=score_dict["ERROR"],
    parsed_report_loop=parsed_report_loop,
    score=score_dict["score"],
    passed=score_dict["result"]
)
        
    path.write(rendered_html)
    
        


    

   

def main():
# Create an ArgumentParser object to handle command-line arguments
    parser = argparse.ArgumentParser(description='Script that starts PMD command')

# Define the expected command-line arguments
    parser.add_argument('file_directory', nargs='+', help='Directory containing files to analyze')
    parser.add_argument('--rulesetpmd', help='Specify a PMD ruleset')
    parser.add_argument('--rulesetsemgrep', help='Specify a Semgrep ruleset')
    parser.add_argument('--out', type=argparse.FileType('w', encoding='UTF-8'), default='score_report.html', help='Specify a path to the output file')

# Parse the command-line arguments
    args = parser.parse_args()

# Extract values from parsed arguments
    fileDirectory= args.file_directory
    path = args.out
    ruleset_pmd = args.rulesetpmd
    ruleset_semgrep = args.rulesetsemgrep
    unparsed_report_pmd = run_pmd(fileDirectory,ruleset_pmd)
    unparsed_report_semgrep = run_semgrep(ruleset_semgrep,fileDirectory)
    parsed_report_pmd = pmd_parser(unparsed_report_pmd,fileDirectory)
    parsed_report_semgrep = semgrep_parser(unparsed_report_semgrep)

    
    report_list = []
    report_list.append(parsed_report_pmd)
    report_list.append(parsed_report_semgrep) 
    
    result= result_dic(report_list)
    score_dict=score_calculator(result)

    print(score_dict["result"])
    html_generator(parsed_report_pmd,parsed_report_semgrep,score_dict,path,fileDirectory)
    


if __name__ == "__main__":
    main()


#
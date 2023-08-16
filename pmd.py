import argparse
import subprocess
import json
import pathlib
from jinja2 import Environment, FileSystemLoader
import os
import subprocess
import xml.etree.ElementTree as ET
import xml.dom.minidom
import sys
from jinja2 import Template
import http.server
import socketserver
import webbrowser

import sys
def run_semgrep(rules,code):
        semgrep_command = [
                "semgrep",
                "--config",
                rules,
                "--junit-xml",
                code,"--quiet"
        ]
        junit_output = subprocess.check_output(semgrep_command )
        
        return (junit_output)


def pmd(fileDirectory,ruleset):
# Construct the command to run PMD
# Split the command and arguments into separate list elements
    command = ['pmd', 'check',"-f","json", fileDirectory, '-R', ruleset,"--no-fail-on-violation"]

    try:
        result = subprocess.run(command,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                text=True,
                                check=True)  # Raise CalledProcessError if command fails

    # Print the captured standard output and standard error
     
        json_content = result.stdout

        # Parse the captured JSON content
        parsed_json = json.loads(json_content)
        
        # Write the parsed JSON to a file (stdout)
        return(parsed_json)


    except subprocess.CalledProcessError as e:
    # Print the error message and captured error output if the command fails
        print("Error:", e)
        print("PMD Error Output:")
        print(e.stderr)
    
def is_windows_path(path):
    
    return '\\' in path

def is_posix_path(path):
    return '/' in path
def normalizer(x):
    match x:
        case 1:
            severity = "ERROR" 
        case 2 | 3:
            severity = "WARNING"
        case 4 | 5:
            severity = "INFO" 

    return severity
def path_normalizer(path):
    
    if is_windows_path(path):
        return pathlib.PureWindowsPath(path).name
    else :
        return pathlib.PurePosixPath(path).name

def pmd_parser(non_parsed_report ):
    
           
        
    
    result_list = []
    result_dict = {"violations": result_list}
    
    for dict in non_parsed_report["files"]:
        for violation in dict['violations']:
            severity = normalizer(violation['priority'])
            dictionary = {
                'file': path_normalizer( dict['filename']),
                'name': violation['rule'],
                'priority': violation['priority'],
                'message': violation['description'],
                'line': violation['beginline'],
                
                'severity': severity
            }
            result_dict['violations'].append(dictionary)
            
    return result_dict
def semgrep_parser(junit_output):
        root = ET.fromstring(junit_output)
        models=root.findall(".//testcase")
        list=[]
        dic = {"violations":list}
        for i in models:
                list.append({"name":i.get('name'),
                        "file":i.get('file'),
                        "line":i.get('line'),
                        "severity":i.find('failure').get('type'),
                        "message":i.find('failure').get('message')
                })
        return (dic)
def score_calculator(report_list):
    warning_count = 0
    info_count = 0
    error_count = 0

    # Read JSON input from stdin and process each JSON object

    for report in report_list:
        violations = report.get("violations", [])
            # Iterate through violations and count severity levels
        for violation in violations:
                
            severity = violation.get("severity", "")
            if severity == "WARNING":
                warning_count += 1
            elif severity == "INFO":
                    info_count += 1
            elif severity == "ERROR":
                    error_count += 1
    dic_score = {"WARNING": warning_count, "INFO": info_count, "ERROR": error_count}
## calculate the score 
    if error_count > 0:
        
        dic_score ["score"] =""

        dic_score ["result"] = False 
        return dic_score
        
    else :
        score= 10 - warning_count - info_count*0.5
        dic_score ["score"] = score
        result = score>=5
        dic_score ["result"] = result 
   
        return dic_score
            
def html_generator(parsed_report_pmd,parsed_report_semgrep,score_dict,path):
    env = Environment(loader=FileSystemLoader('.'))
    template = env.get_template('report.html')
    warning_count = score_dict["WARNING"] 
    info_count = score_dict["INFO"]
    error_count = score_dict["ERROR"]

    
    rendered_html = template.render(
        warning_count=warning_count,
        info_count=info_count,
        error_count=error_count,
        parsed_report_pmd=parsed_report_pmd,
        parsed_report_semgrep=parsed_report_semgrep,  
        score = score_dict["score"],
        passed = score_dict["result"])
    

    # Write the rendered HTML to a file
    path.write(rendered_html)

   
    
def main():
    # Create an ArgumentParser object to handle command-line arguments
    parser = argparse.ArgumentParser(description='Script that starts PMD command')

# Define the expected command-line arguments
    parser.add_argument('file_directory', help='Directory containing files to analyze')
    parser.add_argument('--rulesetpmd', help='Specify a PMD ruleset')
    parser.add_argument('--rulesetsemgrep', help='Specify a Semgrep ruleset')
    parser.add_argument('--out', type=argparse.FileType('w', encoding='UTF-8'), default='score_report.html', help='Specify a path to the output file')

# Parse the command-line arguments
    args = parser.parse_args()

# Extract values from parsed arguments
    fileDirectory = args.file_directory
    path = args.out

    ruleset_pmd = args.rulesetpmd
    ruleset_semgrep = args.rulesetsemgrep
    unparsed_report_pmd = pmd(fileDirectory,ruleset_pmd)
    unparsed_report_semgrep = run_semgrep(ruleset_semgrep,fileDirectory)
    parsed_report_pmd = pmd_parser(unparsed_report_pmd)
    parsed_report_semgrep = semgrep_parser(unparsed_report_semgrep)

    
    report_list = []
    report_list.append(parsed_report_pmd)
    report_list.append(parsed_report_semgrep) 
    score_dict= score_calculator(report_list)
    print(score_dict["result"])
    html_generator(parsed_report_pmd,parsed_report_semgrep,score_dict,path)
    


if __name__ == "__main__":
    main()



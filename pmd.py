import argparse
import subprocess
import json
import os.path
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

ERROR = "ERROR" 
WARNING = "WARNING"
INFO = "INFO" 

def run_tool (command):
    try:
        result = subprocess.run(command,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                text=True,
                                check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print("Error:", e)
        print("Error Output:")
        print(e.stderr)

def run_pmd(fileDirectory,ruleset):
    pmd_command = ['pmd', 'check',"-f","json", fileDirectory, '-R', ruleset,"--no-fail-on-violation"]
    #!!!!!!!!!!!!problem if runtool prints error and returns nothing
    parsed_json = json.loads(run_tool(pmd_command))
    return(parsed_json)

def run_semgrep(rules,code):
    semgrep_command = ["semgrep","--config",rules,"--junit-xml",code,"--quiet"]
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

def pmd_parser(non_parsed_report ):
    violations = []
    for dict in non_parsed_report["files"]:
        for violation in dict['violations']:
            severity = severity_normalizer(violation['priority'])
            dictionary = {
                'file': os.path.basename( dict['filename']),
                'name': violation['rule'],
                'priority': violation['priority'],
                'message': violation['description'],
                'line': violation['beginline'],
                
                'severity': severity
            }
            violations.append(dictionary)    
    return {"violations":violations}

def search_tag(parent,child):
    try:
        return parent.find(child)
    except AttributeError:
        print("check the parent name")
    except TypeError:
        print("check the child name")

def search_tags(parent,child):
    try:
        return parent.findall(child)
    except AttributeError:
        print("check the parent name")
    except TypeError:
        print("check the child name")


def semgrep_parser(junit_output):
        root = ET.fromstring(junit_output)
        models=search_tags(root,".//testcase")
        violations=[]
        for i in models:
                f=search_tag(i,"failure")
                violations.append({"name":i.get('name'),
                        "file":i.get('file'),
                        "line":i.get('line'),
                        "severity":f.get('type'),
                        "message":f.get('message')
                })
        return {"violations":violations}

def result_dic(violations):
    warning_count = 0
    info_count = 0
    error_count = 0
   
    for violation in violations:       
        severity = violation.get("severity", "")
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
    if dic["ERROR"] > 0:
        dic_score ["score"] = 0
        dic_score ["result"] = False 
    else :
        #score could be negative !!!!!!!!!!!
        s=10 - dic["WARNING"]- dic["INFO"]*0.5
        dic_score ["score"] = s > 0 ? s : 0
        dic_score ["result"] = dic_score ["score"]>=5
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
    unparsed_report_pmd = run_pmd(fileDirectory,ruleset_pmd)
    unparsed_report_semgrep = run_semgrep(ruleset_semgrep,fileDirectory)
    parsed_report_pmd = pmd_parser(unparsed_report_pmd)
    parsed_report_semgrep = semgrep_parser(unparsed_report_semgrep)

    
    report_list = []
    report_list.append(parsed_report_pmd)
    report_list.append(parsed_report_semgrep) 
    result= result_dic(report_list)
    score=score_calculator(result)

    print(score)
    html_generator(parsed_report_pmd,parsed_report_semgrep,score_dict,path)
    


if __name__ == "__main__":
    main()

import argparse
import subprocess
import json
from jinja2 import Environment, FileSystemLoader

import sys
def normalizer(x):
    match x:
        case 1:
            severity = "ERROR" 
        case 2 | 3:
            severity = "WARNING"
        case 4 | 5:
            severity = "INFO" 

    return severity

def pmd(fileDirectory,ruleset):
    
    

# Construct the command to run PMD
# Split the command and arguments into separate list elements
    command = ['pmd.bat', 'check',"-f","json", fileDirectory, '-R', ruleset,"--no-fail-on-violation"]

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
    
def json_parser(non_parsed_report ):
    
           
        
    
    result_list = []
    result_dict = {"violations": result_list}
    
    for dict in non_parsed_report["files"]:
        for violation in dict['violations']:
            severity = normalizer(violation['priority'])
            dictionary = {
                'file': dict['filename'],
                'name': violation['rule'],
                'priority': violation['priority'],
                'message': violation['description'],
                'line': violation['beginline'],
                'column': violation['begincolumn'],
                'severity': severity
            }
            result_dict['violations'].append(dictionary)
            
    return result_dict
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
        score = 0
    else :
        score= 10 - warning_count - info_count*0.5
    dic_score ["score"] = score
    result = score>=5
    dic_score ["result"] = result 
   
    return dic_score
            
def html_generator(parsed_report,score_dict,path):
    env = Environment(loader=FileSystemLoader('.'))
    template = env.get_template('report.html')
    warning_count = score_dict["WARNING"] 
    info_count = score_dict["INFO"]
    error_count = score_dict["ERROR"]

    
    rendered_html = template.render(
        warning_count=warning_count,
        info_count=info_count,
        error_count=error_count,
        parsed_report=parsed_report,  
        score = score_dict["score"],
        passed = score_dict["result"])
    

    # Write the rendered HTML to a file
    path.write(rendered_html)

   
    
def main():
    # Create an ArgumentParser object to handle command-line arguments
    parser = argparse.ArgumentParser(description='Script that starts PMD command')

# Define the expected command-line arguments
    parser.add_argument('file_directory', help='Directory containing files to analyze')
    parser.add_argument('--ruleset', help='Specify a PMD ruleset')
    parser.add_argument('--out', type=argparse.FileType('w', encoding='UTF-8'), default='score_report.html', help='Specify a path to the output file')

# Parse the command-line arguments
    args = parser.parse_args()

# Extract values from parsed arguments
    fileDirectory = args.file_directory
    path = args.out

    ruleset = args.ruleset
    unparsed_report = pmd(fileDirectory,ruleset)
    parsed_report = json_parser(unparsed_report)

    
    report_list = []
    report_list.append(parsed_report) 
    score_dict= score_calculator(report_list)
    html_generator(parsed_report,score_dict,path)
    


if __name__ == "__main__":
    main()



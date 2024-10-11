import os
import yaml
import re

def parse_jenkinsfile(jenkinsfile_path):
    stages = {}
    with open(jenkinsfile_path, 'r') as file:
        content = file.readlines()
        
        current_stage = None
        for line in content:
            # Match the stage declaration
            stage_match = re.match(r'\s*stage\s*\'(.*)\'\s*{', line)
            if stage_match:
                current_stage = stage_match.group(1)
                stages[current_stage] = []
            # Skip lines that declare the steps
            elif current_stage and re.match(r'\s*steps\s*{', line):
                continue
            # Collect command lines under the current stage
            elif current_stage:
                command = line.strip()
                # Remove any trailing comments
                command = re.sub(r'\s*//.*$', '', command)
                if command:
                    stages[current_stage].append(command)

    return stages

def generate_github_actions(stages, output_path):
    workflow = {
        'name': 'CI Workflow',
        'on': {
            'push': {
                'branches': ['main']
            },
            'pull_request': {
                'branches': ['main']
            }
        },
        'jobs': {
            'build': {
                'runs-on': 'ubuntu-latest',
                'steps': []
            }
        }
    }

    for stage, commands in stages.items():
        workflow['jobs']['build']['steps'].append({
            'name': stage,
            'run': '\n'.join(commands)
        })

    with open(output_path, 'w') as outfile:
        yaml.dump(workflow, outfile, default_flow_style=False)

def main():
    jenkinsfile_path = 'Jenkinsfile'
    output_path = 'github-actions.yml'
    
    if not os.path.exists(jenkinsfile_path):
        print(f"{jenkinsfile_path} not found.")
        return
    
    stages = parse_jenkinsfile(jenkinsfile_path)
    generate_github_actions(stages, output_path)
    print(f"Generated GitHub Actions workflow at {output_path}")

if __name__ == '__main__':
    main()

import re
import yaml

def convert_jenkinsfile_to_github_actions(jenkinsfile_path, github_actions_path):
    with open(jenkinsfile_path, 'r') as jenkinsfile:
        lines = jenkinsfile.readlines()

    workflow = {
        'name': 'CI',
        'on': ['push'],
        'jobs': {}
    }

    current_stage = None
    for line in lines:
        stage_match = re.match(r'^\s*stage\s*\(\s*\"(.*?)\"\s*\)', line)
        if stage_match:
            current_stage = stage_match.group(1)
            workflow['jobs'][current_stage] = {
                'runs-on': 'ubuntu-latest',
                'steps': []
            }
        elif current_stage:
            sh_match = re.match(r'^\s*sh\s*\(\s*\"(.*?)\"\s*\)', line)
            if sh_match:
                command = sh_match.group(1)
                workflow['jobs'][current_stage]['steps'].append({
                    'name': f'Run {command}',
                    'run': command
                })

    with open(github_actions_path, 'w') as github_actions_file:
        yaml.dump(workflow, github_actions_file, default_flow_style=False)

# Example usage
convert_jenkinsfile_to_github_actions('Jenkinsfile', '.github/workflows/main.yml')

import yaml
import re

def parse_jenkinsfile(jenkinsfile_path):
    stages = []
    with open(jenkinsfile_path, 'r') as file:
        lines = file.readlines()

    stage_pattern = re.compile(r'stage\s*\'([^\']+)\'')
    steps_pattern = re.compile(r'steps\s*{([^}]*)}')

    current_stage = None
    for line in lines:
        stage_match = stage_pattern.search(line)
        steps_match = steps_pattern.search(line)

        if stage_match:
            if current_stage:
                stages.append(current_stage)
            current_stage = {
                'name': stage_match.group(1),
                'steps': []
            }

        if steps_match and current_stage:
            steps_content = steps_match.group(1).strip().split('\n')
            for step in steps_content:
                step = step.strip()
                if step:
                    current_stage['steps'].append(step)

    if current_stage:
        stages.append(current_stage)

    return stages

def generate_github_actions(stages):
    workflow = {
        'name': 'Jenkins to GitHub Actions Workflow',
        'on': {'push': {'branches': ['main']}},
        'jobs': {}
    }

    for stage in stages:
        job_id = re.sub(r'\s+', '_', stage['name']).lower()
        workflow['jobs'][job_id] = {
            'runs-on': 'ubuntu-latest',
            'steps': []
        }
        
        for step in stage['steps']:
            workflow['jobs'][job_id]['steps'].append({
                'name': step,
                'run': step  # Adjust this as necessary for the specific command
            })

    return workflow

def save_to_yaml(workflow, output_path):
    with open(output_path, 'w') as file:
        yaml.dump(workflow, file, default_flow_style=False)

def main():
    jenkinsfile_path = 'Jenkinsfile'  # Path to your Jenkinsfile
    output_path = 'github_actions_workflow.yml'  # Output file path

    stages = parse_jenkinsfile(jenkinsfile_path)
    workflow = generate_github_actions(stages)
    save_to_yaml(workflow, output_path)
    print(f'GitHub Actions workflow saved to {output_path}')

if __name__ == '__main__':
    main()

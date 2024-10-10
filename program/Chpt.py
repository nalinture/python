import re
import yaml

def parse_jenkinsfile(jenkinsfile_content):
    """Extract stages and steps from a Jenkinsfile."""
    stages = []
    stage_pattern = re.compile(r'stage\s*\'([^\']+)\'\s*{([^}]+)}', re.DOTALL)

    for match in stage_pattern.finditer(jenkinsfile_content):
        stage_name = match.group(1).strip()
        stage_steps = match.group(2).strip()
        steps = parse_steps(stage_steps)
        stages.append({'name': stage_name, 'steps': steps})

    return stages

def parse_steps(steps_content):
    """Extract steps from a stage."""
    steps = []
    sh_pattern = re.compile(r'sh\s*\'([^\']+)\'')
    script_pattern = re.compile(r'script\s*{([^}]+)}', re.DOTALL)

    # Find 'sh' commands
    for match in sh_pattern.finditer(steps_content):
        steps.append({'run': match.group(1).strip()})

    # Find 'script' blocks
    for match in script_pattern.finditer(steps_content):
        inner_steps = match.group(1).strip()
        steps += parse_steps(inner_steps)

    return steps

def convert_to_github_actions(stages):
    """Convert stages to GitHub Actions workflow format."""
    jobs = {
        'build': {
            'runs-on': 'ubuntu-latest',
            'steps': [{'name': 'Checkout code', 'uses': 'actions/checkout@v2'}]
        }
    }

    # Adding steps from Jenkins stages
    for stage in stages:
        for step in stage['steps']:
            jobs['build']['steps'].append(step)
    
    return {
        'name': 'CI Workflow',
        'on': {
            'push': {},
            'pull_request': {}
        },
        'jobs': jobs
    }

def write_yaml_to_file(data, filename):
    """Write the generated data to a YAML file."""
    with open(filename, 'w') as file:
        yaml.dump(data, file, default_flow_style=False)

if __name__ == "__main__":
    jenkinsfile_path = 'Jenkinsfile'  # Path to the Jenkinsfile
    output_yaml_path = '.github/workflows/ci.yml'  # Output path for GitHub Actions

    # Read Jenkinsfile
    with open(jenkinsfile_path, 'r') as file:
        jenkinsfile_content = file.read()

    # Parse Jenkinsfile
    stages = parse_jenkinsfile(jenkinsfile_content)

    # Convert to GitHub Actions format
    github_actions_workflow = convert_to_github_actions(stages)

    # Write to YAML file
    write_yaml_to_file(github_actions_workflow, output_yaml_path)

    print(f"GitHub Actions workflow written to {output_yaml_path}")
  

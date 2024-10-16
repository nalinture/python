import re
import yaml

def extract_stages(jenkinsfile_content):
    stage_pattern = re.compile(r"stage\('([^']+)'\) \{(.*?)\}", re.DOTALL)
    return stage_pattern.findall(jenkinsfile_content)

def extract_steps(stage_content):
    steps_pattern = re.compile(r"steps \{(.*?)\}", re.DOTALL)
    steps_match = steps_pattern.search(stage_content)
    if not steps_match:
        raise ValueError("Steps not found in stage.")
    return steps_match.group(1)

def convert_step_to_github_action(step):
    # Convert Jenkins step to GitHub Actions step
    if "sh" in step:
        script = re.search(r"sh \(returnStdout: true, script: '''(.*?)''' \)", step, re.DOTALL).group(1)
        return {
            "name": "Run shell script",
            "run": script.strip().strip("'''")
        }
    elif "configFileProvider" in step:
        return {
            "name": "Download configuration file",
            "run": "aws s3 cp s3://your-bucket/nuget-managed-config ${{ github.workspace }}/nuget-managed-config"
        }
    elif "container" in step:
        return {
            "name": "Set up Docker",
            "run": "sudo apt-get install -y docker.io && sudo systemctl start docker"
        }
    # Add more conversions as needed
    return None

def generate_github_actions_yaml(stages):
    jobs = {}
    for stage_name, stage_content in stages:
        steps_content = extract_steps(stage_content)
        steps = steps_content.split("\n")
        github_steps = []

        for step in steps:
            github_step = convert_step_to_github_action(step)
            if github_step:
                github_steps.append(github_step)

        job_name = stage_name.lower().replace(' ', '-')
        jobs[job_name] = {
            "runs-on": "ubuntu-latest",
            "steps": github_steps
        }

    workflow = {
        "name": "CI Pipeline",
        "on": {
            "push": {
                "branches": ["main"]
            },
            "pull_request": {}
        },
        "jobs": jobs
    }
    return yaml.dump(workflow, sort_keys=False)

def convert_to_github_actions(jenkinsfile_path, output_path):
    with open(jenkinsfile_path, 'r') as file:
        jenkinsfile_content = file.read()

    stages = extract_stages(jenkinsfile_content)
    github_actions_content = generate_github_actions_yaml(stages)

    with open(output_path, 'w') as file:
        file.write(github_actions_content)

    print(f"GitHub Actions workflow has been written to {output_path}")

# Example usage
convert_to_github_actions('Jenkinsfile', '.github/workflows/ci-pipeline.yml')

def parse_jenkinsfile(jenkinsfile_path):
    stages = []
    try:
        with open(jenkinsfile_path, 'r') as file:
            lines = file.readlines()
    except FileNotFoundError:
        print(f"Error: The file {jenkinsfile_path} was not found.")
        return stages

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

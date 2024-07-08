import yaml

def extract_yaml(yaml_text):
    yaml_text= yaml_text.strip()
    yaml_text = yaml_text.split('\n```')[0]
    
    # Remove the triple backticks
    if yaml_text.startswith('```yaml'):
        yaml_text = yaml_text[7:].strip()
    
    yaml_data = yaml.safe_load(yaml_text)
    return yaml_data
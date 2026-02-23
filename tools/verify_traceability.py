import yaml
import sys

def verify_traceability(req_yaml_path, plan_yaml_path):
    with open(req_yaml_path, 'r', encoding='utf-8') as f:
        req_data = yaml.safe_load(f)
    with open(plan_yaml_path, 'r', encoding='utf-8') as f:
        plan_data = yaml.safe_load(f)
    
    plan_ids = {item['id'] for item in plan_data['section']['items']}
    
    missing_traces = []
    for req in req_data['requirements_document']['functional_requirements']:
        if req.get('derived_from') not in plan_ids:
            missing_traces.append(req['req_id'])
    
    if missing_traces:
        print(f"TRACEABILITY: FAIL - Missing traces: {missing_traces}")
        sys.exit(1)
    else:
        print("TRACEABILITY: PASS")
        sys.exit(0)

if __name__ == "__main__":
    verify_traceability(sys.argv[1], sys.argv[2])

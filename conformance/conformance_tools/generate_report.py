"""
Module to generate conformance report
requires bikeshed to be installed
"""
import os

from bs4 import BeautifulSoup
from .utils import dump_to_json, execute_cmd, read_json

SPECIFICATION = 'av1isobmff'
EXCLUDED_RULES = []


def get_coverage_data(rules_from_spec, rules_from_files):
    '''
    For each spec rule add matched file entries with descriptions
    '''
    coverage_data = []

    for rule_spec in rules_from_spec:
        rule_coverage = {
            'id': rule_spec['id'],
            'description': rule_spec['description'],
            'exclude': rule_spec['id'] in EXCLUDED_RULES,
            'successful_checks': [],
            'errors': [],
            'warnings': []
        }

        for rule_file in rules_from_files:
            for check_type in ['successful_checks', 'errors', 'warnings']:
                found_files = set()
                for check in rule_file[check_type]:
                    if check['id'] == rule_spec['id']:
                        if rule_file['file_path'] in found_files:
                            print(f"WARNING: Duplicate file found for {check['id']} within {rule_file['file_path']}")
                            continue
                        rule_coverage[check_type].append({
                            'file_path': rule_file['file_path'],
                            'invalid': rule_file['invalid'],
                            'description': check['description']
                        })
                        found_files.add(rule_file['file_path'])

        coverage_data.append(rule_coverage)
    return coverage_data


def filter_validation_entries(spec_validation):
    '''
    Make sure that each validation entry has id, details and description only
    '''
    for key in ['successful_checks', 'errors', 'warnings', 'unchecked']:
        filtered_list = []
        for item in spec_validation[key]:
            if 'id' in item:
                filtered_item = {
                    'id': item.get('id', None),
                    'details': item.get('details', None),
                    'description': item.get('description', None)
                }
                filtered_list.append(filtered_item)
        spec_validation[key] = filtered_list
        if 'specification' in spec_validation:
            del spec_validation['specification']
    return spec_validation


def duplicate_spec_rules_found(rules):
    '''
    Check if for all rules the assert-id's are unique
    '''
    descriptions = {}
    duplicates_found = False
    for rule in rules:
        desc = rule['description']
        if desc in descriptions:
            descriptions[desc][0] += 1
            duplicates_found = True
        else:
            descriptions[desc] = [1, rule['id']]

    if duplicates_found:
        print("ATTENTION: Duplicate rules found. See CSV below")
        print("assert-id,description")
        for description, info in descriptions.items():
            if info[0] > 1:
                print(f"{info[1]},{description.replace(',', ';')}")

    return duplicates_found

def duplicate_cw_versions_found():
    '''
    Check if conformance files contain more than one cw version
    '''
    cw_versions = set()
    for root, _subdirs, files in os.walk('conformance_files'):
        for conf_file in files:
            _input_filename, input_extension = os.path.splitext(conf_file)
            if input_extension not in ['.json']:
                continue
            input_path = os.path.join(root, conf_file)

            json_string = read_json(input_path)

            cw_versions.add(json_string['compliance_warden']['cw_version'])

    if len(cw_versions) > 1:
        return True, None
    return False, cw_versions.pop()


def get_rules_from_spec():
    '''
    Compile the spec using bikeshed command and extract a list of rules
    [{'id': '...', 'description': '...'}, ]
    '''
    ret = execute_cmd('bikeshed spec ../index.bs temp.html')

    if ret.returncode != 0:
        print('Could not execute bikeshed')
        return None
    with open('temp.html', 'r', encoding='utf-8') as spec_file:
        soup = BeautifulSoup(spec_file, features="lxml")
    os.remove('temp.html')
    assert_spans = soup.find_all('span',
                                 {'id': lambda L: L and L.startswith('assert-')})

    rules = []
    for assert_span in assert_spans:
        rules.append({'id': assert_span.get('id'),
                      "description": assert_span.text.replace('"', '')})
    return rules


def get_rules_from_files(spec):
    '''
    Get rules from the file json's
    '''
    rules_from_files = []
    for root, _subdirs, files in os.walk('conformance_files'):
        for conf_file in files:
            _input_filename, input_extension = os.path.splitext(conf_file)
            if input_extension not in ['.json']:
                continue
            input_path = os.path.join(root, conf_file)

            json_string = read_json(input_path)
            conformance_path = os.path.relpath(os.path.join(root, json_string["path"]))

            cw_report = json_string['compliance_warden']
            if not cw_report:
                continue

            for spec_validation in cw_report['validation']:
                if spec_validation['specification'] != spec:
                    continue
                spec_validation = filter_validation_entries(spec_validation)
                spec_validation['file_path'] = conformance_path
                spec_validation['invalid'] = len(spec_validation['errors']) > 0
                rules_from_files.append(spec_validation)
    return rules_from_files


def print_coverage_stats(coverage_data):
    total_rules = len(coverage_data)
    covered_rules = 0
    uncovered_rules = []

    for rule in coverage_data:
        print(f'Rule id: {rule["id"]}')
        print(f'Description: {rule["description"]}')

        total_checks = 0
        for check_type in ['successful_checks', 'errors', 'warnings']:
            total_checks += len(rule[check_type])
            if rule[check_type]:
                print(f"{check_type}:")
                for check in rule[check_type]:
                    print(f'\tFile path: {check["file_path"]}')
                    print(f'\tDescription: {check["description"]}')

        if total_checks > 0:
            covered_rules += 1
        else:
            uncovered_rules.append(rule['id'])

        print("\n")

    print(f'Overall coverage (w/o exclusions): {(covered_rules/total_rules)*100}%')
    print(f'Uncovered rules: {uncovered_rules}')


def main():
    """Entry point"""
    rules_from_spec = get_rules_from_spec()
    # Abort if there are rules with the same id.
    if duplicate_spec_rules_found(rules_from_spec):
        print("Make sure the assert-id's are unique for every rule!")
        return -1
    # Abort if there are more than one cw version
    duplicate_cw, cw_version = duplicate_cw_versions_found()
    if duplicate_cw:
        print("Make sure there is only one version of Compliance Warden!")
        return -1
    # get data from file json's for this specification
    rules_from_files = get_rules_from_files(spec=SPECIFICATION)
    # build coverage data
    coverage_data = get_coverage_data(rules_from_spec, rules_from_files)
    coverage_data = {
        'cw_version': cw_version,
        'rules': coverage_data
    }
    # store and print
    print_coverage_stats(coverage_data["rules"])
    dump_to_json('coverage.json', coverage_data)

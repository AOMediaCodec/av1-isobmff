"""
Module to manage files of the conformance suite
"""
import argparse
import copy
import json
import os
import shutil
import sys

from .utils import (compute_file_md5, dump_to_json, execute_cmd,
                    make_dirs_from_path, read_json)

SPECIFICATION = 'av1isobmff'

FILE_ENTRY = {
    'contributor': '',
    'description': '',
    'md5': '',
    'version': 1,
    'associated_files': [],
    'notes': '',
    'license': ''
}

# ignore files with the following extensions
INCLUDELIST = ['.bin', '.mp4', '.obu']


def update_validation(args):
    '''
    Update validation metadata for all files
    '''
    for root, _subdirs, files in os.walk('./conformance_files'):
        for conf_file in files:
            input_filename, input_extension = os.path.splitext(conf_file)
            if input_extension not in INCLUDELIST:
                continue
            input_path = os.path.join(root, conf_file)
            prefix, ext = os.path.splitext(input_path)
            input_json = prefix + '.json'
            file_meta = read_json(input_json)
            cw_out = run_compliance_warden(args.complianceWarden, input_path)
            file_meta['compliance_warden'] = cw_out
            dump_to_json(input_json, file_meta)


def run_compliance_warden(cwexe_path, input_file):
    """run cw.exe"""
    res = execute_cmd(f'{cwexe_path} -s {SPECIFICATION} -f json {input_file}')
    return json.loads(res.stdout.decode())


def process_files(args, output_root, contributor, license_str):
    """Process conformance files"""
    cnt = 0
    for root, _subdirs, files in os.walk(args.input):
        for conf_file in files:
            input_filename, input_extension = os.path.splitext(conf_file)
            if input_extension not in INCLUDELIST:
                continue
            input_path = os.path.join(root, conf_file)
            if ' ' in input_path:
                print(
                    f'ERROR: spaces are not allowed. Remove spaces in "{input_path}"')
                sys.exit(-1)

            output_dir = os.path.join(
                output_root, os.path.relpath(root, args.input))
            json_path = os.path.join(output_dir, input_filename + '.json')
            output_path = os.path.join(output_dir, conf_file)

            print(f'\n* Processing: "{input_path}"')
            md5 = compute_file_md5(input_path)

            file_meta = None
            version = 1
            if os.path.exists(json_path) and not args.force:
                existing_meta = read_json(json_path)
                if existing_meta['md5'] == md5:
                    print('skip duplicate file.')
                    continue
                print(f'* new file version detected for {conf_file}')
                file_meta = existing_meta
                version = file_meta['version'] + 1
                description = file_meta['description']

            make_dirs_from_path(output_dir)
            shutil.copyfile(input_path, output_path)
            if file_meta is None:
                description = input(
                    f'* Provide short description for "{conf_file}": ')
            else:
                new_description = input(
                    f'* Update description for "{conf_file}" (leave blank to keep previous): ')
                if len(new_description) > 0:
                    description = new_description

            cw_out = run_compliance_warden(args.complianceWarden, input_path)
            if file_meta is None:
                file_meta = copy.deepcopy(FILE_ENTRY)
            file_meta['contributor'] = contributor.strip()
            file_meta['path'] = os.path.join('./', conf_file)
            file_meta['md5'] = md5
            file_meta['description'] = description
            file_meta['notes'] = ''
            file_meta['version'] = version
            file_meta['license'] = license_str
            file_meta['compliance_warden'] = cw_out
            dump_to_json(json_path, file_meta)
            cnt += 1
    print(f'Processed {cnt} files.')


def main():
    """Entry point"""
    parser = argparse.ArgumentParser(
        description='Contribute new files to the conformance suite')
    parser.add_argument('-i', '--input',
                        help='Input directory with new files')
    parser.add_argument('-l', '--license',
                        help='Path to a .txt file with a license')
    parser.add_argument('-e', '--complianceWarden',
                        help='Path to Compliance Warden executable cw.exe',
                        required=True)
    parser.add_argument('--force',
                        help='Force run the script if files already exist.',
                        action='store_true')
    parser.add_argument('--update',
                        help='Run cw.exe on all files and update validation.',
                        action='store_true')
    args = parser.parse_args()

    if args.update:
        update_validation(args)
        sys.exit(0)

    license_str = ''
    if args.license is None:
        print("WARNING: You didn't provide a license for files you want to contribute.")
        response = input(' Are you sure you want to continue? (y - yes): ')
        if not response == 'y' and not response == 'yes':
            print('Abort')
            sys.exit(1)
    else:
        with open(args.license, 'r', encoding='utf-8') as file:
            license_str = file.read()

    print('Add (or update) conformance files in "conformance_files" folder.\n')
    contributor = input('Your company name: ')

    # get rid of the last slash if needed
    if args.input[-1] == '/':
        args.input = args.input[:-1]
    if not os.path.isdir(args.input):
        print('ERROR: input should be a directory')
        sys.exit(-1)
    _input_base, input_last_folder = os.path.split(args.input)
    output_root = os.path.join('./conformance_files', input_last_folder)

    print(f'Process files from "{input_last_folder}".')

    process_files(args, output_root, contributor, license_str)

# coding:utf-8

import os
import shutil
import subprocess
import argparse
import sys


class FileCategorizer:
    def __init__(self, root_dir):
        self.root_dir = root_dir
        self.file_list_filename = 'file_list.txt'
        self.file_info_filename = 'file_info.txt'
        self.parse_result_filename = 'file_parse_result.txt'
        self.result_root_dir = './result'
        self.copy_log_filename = 'file_copy_log.txt'

    def collect_file(self):
        file_path_list = []
        for dirpath, dirnames, filenames in os.walk(self.root_dir):
            for filename in filenames:
                if '.' in filename:
                    continue
                file_path_list.append(os.path.join(dirpath, filename))
        with open(self.file_list_filename, 'w', newline='\n', encoding='utf-8') as f:
            f.write('\n'.join(file_path_list))

    def gen_file_info(self):
        process = subprocess.run('file -f {}'.format(self.file_list_filename), capture_output=True, text=True,
                                 encoding='utf-8')
        with open(self.file_info_filename, 'w', newline='\n', encoding='utf-8') as f:
            f.write(process.stdout)

    def parse_file_info(self):
        f_info = open(self.file_info_filename, encoding='utf-8')
        f_file = open(self.file_list_filename, encoding='utf-8')
        f_result = open(self.parse_result_filename, 'w', encoding='utf-8')
        file_path_set = set()
        result_root_dir = self.result_root_dir
        for file, info in zip(f_file, f_info):
            file = file.strip()
            info = info.strip()
            info_name, _, info_detail = info.partition(':')
            assert info_name == file, 'info_name({}) file({})'.format(info_name, file)
            info_detail = info_detail.strip().lower()
            unknown = False
            if 'ogg' in info_detail:
                extension = 'ogg'
            elif 'png' in info_detail:
                extension = 'png'
            elif 'json' in info_detail:
                extension = 'json'
            elif 'asf' in info_detail:
                extension = 'wmv'
            elif 'text' in info_detail:
                extension = 'txt'
            else:
                extension = ''
                unknown = True
            dir_name, file_name = os.path.split(info_name)
            _, src_dir = os.path.split(dir_name)
            if unknown:
                new_file_name = '{}_{}'.format(src_dir, file_name)
                result_dir = os.path.join(result_root_dir, 'unknown')
            else:
                new_file_name = '{}_{}.{}'.format(src_dir, file_name, extension)
                result_dir = os.path.join(result_root_dir, extension)
            new_file_path = os.path.join(result_dir, new_file_name)
            assert new_file_path not in file_path_set, new_file_path
            file_path_set.add(new_file_path)
            f_result.write('|'.join([info_name, info_detail, new_file_name, new_file_path]))
            f_result.write('\n')
        f_result.close()
        f_file.close()
        f_info.close()

    def copy_file_to_result_dir(self):
        f_log = open(self.copy_log_filename, 'w')
        with open(self.parse_result_filename, encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                old_path, _, _, new_path = line.split('|')
                new_dir, _ = os.path.split(new_path)
                if not os.path.exists(new_dir):
                    os.makedirs(new_dir)
                shutil.copy(old_path, new_path)
                f_log.write('{}    ->    {}\n'.format(old_path, new_path))
        f_log.close()

    def autorun(self):
        self.collect_file()
        self.gen_file_info()
        self.parse_file_info()
        self.copy_file_to_result_dir()


if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('op')
    arg_parser.add_argument('root', default='./')
    args = arg_parser.parse_args(sys.argv[1:])
    op = args.op
    categorizer = FileCategorizer(args.root)
    if op == 'collect':
        categorizer.collect_file()
    elif op == 'gen':
        categorizer.gen_file_info()
    elif op == 'parse':
        categorizer.parse_file_info()
    elif op == 'copy':
        categorizer.copy_file_to_result_dir()
    elif op == 'autorun':
        categorizer.autorun()

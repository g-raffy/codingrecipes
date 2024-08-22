#!/usr/bin/env python3
from typing import List
import subprocess
from pathlib import Path
import logging


class CommandRunner():
    target_machine_fqdn: str

    def __init__(self, target_machine_fqdn: str):
        self.target_machine_fqdn = target_machine_fqdn

    def run_commands(self, commands: List[str], work_dir: Path = None, abort_on_error=True) -> subprocess.CompletedProcess:
        logging.debug('running %s on %s', commands, self.target_machine_fqdn)
        bash_commands = commands
        if work_dir is not None:
            bash_commands.insert(0, f'cd {work_dir}')
        bash_commands_as_str = ' && '.join(bash_commands)
        bash_commands_as_str = bash_commands_as_str.replace('$', '\\$')
        print(bash_commands_as_str)
        completed_process = subprocess.run(f'ssh {self.target_machine_fqdn} "{bash_commands_as_str}"', shell=True, check=abort_on_error, executable='/bin/bash', capture_output=True)
        if abort_on_error:
            if completed_process.returncode != 0:
                logging.error('the command %s failed on %s with the following errors:', bash_commands_as_str, self.target_machine_fqdn)
                logging.error(completed_process.stderr.decode())
                assert False
        return completed_process


def main():
    logging.basicConfig(level=logging.DEBUG)

    target_machine_fqdn = 'alambix97.ipr.univ-rennes.fr'
    expe_tmp_dir = Path('/opt/ipr/cluster/work.local/graffy/codingrecipes/experimentations/expe0001')
    command_runner = CommandRunner(target_machine_fqdn)
    command_runner.run_commands([f'mkdir -p {expe_tmp_dir}'])

    subprocess.run(f'rsync -va ./ {target_machine_fqdn}:{expe_tmp_dir}/', shell=True, check=True)

    exe_name = 'dgemm_test'
    requested_mkl_version = 'latest'
    mkl_lib = 'mkl-dynamic-lp64-gomp'
    logging.info('building %s against mkl library %s version %s', exe_name, mkl_lib, requested_mkl_version)
    build_commands = [
        'source /etc/profile.d/modules.sh',
        f'module load lib/mkl/{requested_mkl_version}',
        'pwd',
        f'echo compilation cflags: $(pkgconf --cflags {mkl_lib})',
        f'gcc -c $(pkgconf --cflags {mkl_lib}) dgemm_test.c',
        f'gcc -o {exe_name} $(pkgconf --libs {mkl_lib}) dgemm_test.o',
    ]
    completed_process = command_runner.run_commands(build_commands, work_dir=expe_tmp_dir)
    logging.debug(completed_process.stdout.decode())

    logging.info('show that the executable doesn\'t use libiomp5')
    completed_process = command_runner.run_commands([
        'source /etc/profile.d/modules.sh',
        f'module load lib/mkl/{requested_mkl_version}',
        f'ldd {exe_name}'], work_dir=expe_tmp_dir)
    logging.debug(completed_process.stdout.decode())

    logging.info('run %s to make sure that it works in multithreaded mode', exe_name)
    matrix_size = 1024
    min_run_duration = 3  # in seconds
    completed_process = command_runner.run_commands([
        'source /etc/profile.d/modules.sh',
        f'module load lib/mkl/{requested_mkl_version}',
        f'./{exe_name} {matrix_size} {min_run_duration}'], work_dir=expe_tmp_dir)
    logging.debug(completed_process.stdout.decode())


main()

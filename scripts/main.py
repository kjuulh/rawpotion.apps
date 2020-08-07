#!/usr/bin/env python

import click
import yaml
import json
import os
import subprocess

from pathlib import Path


def find_services(file_path):
    with open(file_path, 'r') as stream:
        try:
            runnable = yaml.safe_load(stream)
            if runnable:
                return runnable['services']
            else:
                return None
        except yaml.YAMLError as exc:
            print(exc)


def get_runnables(file_path, services):
    runnables = []
    for service_key, service_values in services.items():
        environments = service_values['environments']
        runnables.append({
            "path": str(file_path),
            "service": service_key,
            "environments": environments,
        })
    return runnables


def filter_exclude(runnables, exclude):
    filtered_runnables = []
    services_to_exclude = exclude.split(',')
    for runnable in runnables:
        if runnable['service'] not in services_to_exclude:
            filtered_runnables.append(runnable)
    return filtered_runnables


def run_command(runnables, environment):
    primary_path = os.getcwd()
    for runnable in runnables:
        os.chdir(Path(runnable['path']).parent)
        command = runnable['environments'][environment]['command']
        print("{}::{}".format(runnable['service'], command))
        # os.system(command)
        print(command)
        os.system("gnome-terminal -e 'bash -c \"{}\"'".format(command))
        os.chdir(primary_path)


def runnable(relative, environment,  exclude, include):
    print("Finding all files for relative =", relative)
    rel_path = Path(relative)
    runnable_files = rel_path.glob("**/runnable.yaml")
    if include:
        files_to_include = include.split(',')
        runnable_files = list(runnable_files).extend(files_to_include)

    runnables = []
    for runnable_file in runnable_files:
        services = find_services(runnable_file)
        if services:
            runnables.extend(get_runnables(runnable_file, services))
    runnables = filter_exclude(runnables, exclude)
    run_command(runnables, environment)


@click.command()
@click.option('--relative', default=".", help="the relative path which the script should run")
@click.option('--environment', default="dev", help="the environment command to run, set in runnable.yaml")
@click.option('--exclude', default="",  help="a comma seperated list of services to exclude")
@click.option('--include', default="", help="a comma seperated list of services to include")
def main(relative, environment, exclude, include):
    runnable(relative, environment, exclude, include)


if __name__ == '__main__':
    main()

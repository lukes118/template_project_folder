import itertools
import toml
import numpy as np
import os
import datetime

def write_toml_files(master_config, path_to_job):
    path_to_save = os.path.join(path_to_job, 'data')
    os.mkdir(path_to_save)

    path_to_config = os.path.join(path_to_job, 'config')
    os.mkdir(path_to_config)

    print("writing config files to: ", path_to_config)
    # getting combinations and writing other config files
    group_labels = []; param_labels = []; params = []
    for group_name, group in master_config.items():
        for key, value in group.items():
            if type(value) == list:
                group_labels.append(group_name)
                param_labels.append(key)
                params.append(value)

    param_combinations = list(itertools.product(*params))
    n_jobs = len(param_combinations)
    print(f'n_jobs = {n_jobs}')

    # writing master config file to toml
    master_config_file = os.path.join(path_to_config, 'config_master.toml')
    with open(master_config_file, 'w') as f:
        master_config["misc"]["n_jobs"] = n_jobs
        toml.dump(master_config, f)

    # making config for each parameter combination
    for s, param_set in enumerate(param_combinations):
        sub_config = master_config

        # changing arrays to specific values
        for k, param in enumerate(param_set):
            sub_config[group_labels[k]][param_labels[k]] = param
        save_file = os.path.join(path_to_save, f'data_{s}.h5')
        sub_config['files']['save_file'] = save_file

        # saving to toml
        config_file = os.path.join(path_to_config, f'config_{s}.toml')
        with open(config_file, 'w') as f:
            toml.dump(sub_config, f)


def write_job_script(slurm_kwargs, path_to_job):
    # writing slurm script
    print("making submission script...")
    submission_script = os.path.join(path_to_job, "job_script.sh")

    path_to_out_files = os.path.join(path_to_job, 'out')
    os.mkdir(path_to_out_files)

    out_file = os.path.join(path_to_out_files, '%j.out')
    err_file = os.path.join(path_to_out_files, '%j.err')
    job_status_file = os.path.join(path_to_out_files, 'job_status_$SLURM_ARRAY_TASK_ID.txt')

    mail = ''
    if slurm_kwargs["mail"]:
        mail = f'#SBATCH --mail-type={slurm_kwargs["mail"]}'

    lines = [
        '#!/bin/bash',
        f'#SBATCH --partition={slurm_kwargs["partition"]}',
        f'#SBATCH --time={slurm_kwargs["time"]}',
        f'#SBATCH --mem-per-cpu={slurm_kwargs["mem"]}',
        f'#SBATCH --ntasks=1',
        f'#SBATCH --cpus-per-task={slurm_kwargs["cpus"]}',
        f'#SBATCH --job-name={slurm_kwargs["job_name"]}',
        f'#SBATCH --array=0-{slurm_kwargs["n_jobs"]-1}',
        f'#SBATCH --output={out_file}',
        f'#SBATCH --error={err_file}',
        mail,
        'set -e',
        'export scratch="/scratch/$USER/$SLURM_JOB_ID"',
        'export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK\n',
        'mkdir -p $scratch',
        'cd $scratch',
        f'module load {slurm_kwargs["modules"]}',
        f'echo $SLURM_JOB_ID > {job_status_file}',
        f'srun {slurm_kwargs["srun"]}',
        f'echo "done." > {job_status_file}',

        f'cd',
        f'rm -rf $scratch',
        'exit 0',
    ]
    with open(submission_script, "w") as f:
        f.writelines("\n".join(lines))

def write_job_script_mac(run_kwargs, path_to_job):
    job_script = os.path.join(path_to_job, "job_script.sh")
    print("writing a job script to loop through tasks")
    lines = [
        "echo running job ... ",
        run_kwargs["run"],
        "echo finished running ... ",
    ]
    with open(job_script, 'w') as f:
        f.writelines("\n".join(lines))



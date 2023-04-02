import os
import numpy as np
import toml
import itertools
import copy
class job:
    def __init__(self, job_name, project_name):
        self.job_name = job_name
        self.project_name = project_name

    def set_project_dir(self, path):
        self.project_dir = path
        if not os.path.exists(path):
            print("Could not create job: project dir does not exist")
            exit(1)
    def set_job_dir(self, path):
        self.job_dir = path
        os.mkdir(path)

    def set_exe(self, path, program = ''):
        self.exe_path = path
        self.exe_name = path.split("/")[-1]
        self.program = program


    def set_config(self, config):
        self.config = config

        # converting numpy arrays
        for group_label, group in config.items():
            for label, param in group.items():
                if type(param) == np.ndarray:
                   print(f"converting {label} to list of floats")
                   self.config[group_label][label] = [float(x) for x in param]

        save_dir = os.path.join(self.job_dir, 'data')
        os.mkdir(save_dir)

        config_dir = os.path.join(self.job_dir, 'config')
        os.mkdir(config_dir)

        # getting combinations for lists in config
        group_labels = []; param_labels = []; params = []
        for group_name, group in config.items():
            for key, value in group.items():
                if type(value) == list:
                    group_labels.append(group_name)
                    param_labels.append(key)
                    params.append(value)

        param_combinations = list(itertools.product(*params))
        self.n_jobs = len(param_combinations)

        # writing master config file to toml
        print('writing config files... ')
        master_config_file = os.path.join(config_dir, 'config_master.toml')
        with open(master_config_file, 'w') as f:
            if 'misc' in self.config:
                self.config["misc"]["n_jobs"] = self.n_jobs
                toml.dump(self.config, f)
            else:
                self.config["misc"] = {'n_jobs': self.n_jobs}
                toml.dump(self.config, f)

        # making config for each parameter combination
        for s, param_set in enumerate(param_combinations):
            sub_config = copy.deepcopy(self.config)

            # changing arrays to specific values
            for k, param in enumerate(param_set):
                sub_config[group_labels[k]][param_labels[k]] = param

            if 'files' in self.config:
                if 'save_file' in sub_config['files']:
                    sub_config['files']['save_file'] = os.path.join(
                        save_dir, number_file(self.config["files"]["save_file"], s, self.n_jobs),)

            # saving to toml
            config_file = os.path.join(config_dir, number_file("config.toml", s, self.n_jobs))
            with open(config_file, 'w') as f:
                toml.dump(sub_config, f)

    def set_slurm_kwargs(self, slurm_kwargs):
        self.slurm_kwargs = slurm_kwargs
        # TODO: make this work with padding
        # writing slurm script
        print("making submission script...")
        submission_script = os.path.join(self.job_dir, "slurm_script.sh")

        path_to_out_files = os.path.join(self.job_dir, 'out')
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
            f'#SBATCH --job-name={self.job_name}',
            f'#SBATCH --array=0-{self.n_jobs-1}',
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
            f'srun {self.program} {self.exe_path} '
                f'{os.path.join(self.job_dir, "config", "config_$SLURM_ARRAY_TASK_ID.toml")}',
            f'echo "done." > {job_status_file}',

            f'cd',
            f'rm -rf $scratch',
            'exit 0',
        ]
        with open(submission_script, "w") as f:
            f.writelines("\n".join(lines))

    def write_job_script(self,  padding = False):
        # scripts to loop through jobs
        # TODO: write for padding as wellob_script = os.path.join(path_to_job, "job_script.sh")


        print("writing a job script to loop through jobs... ")
        job_range = "{0.." + str(self.n_jobs) + "}"
        if padding == True:
            lines = [
                f'for i in $(seq -f "%0{len(str(self.n_jobs))}g" 0 {self.n_jobs-1})',
                '   do',
                f'       julia {self.exe_path} {self.job_dir}/config/config.$i.toml',
                '   done',
            ]
        else:
            lines = [
                f'for i in {{0..{self.n_jobs-1}}}; do',
                f'{self.program} {self.exe_path} {os.path.join(self.job_dir, "config", "config_$i.toml")}',
                'done'
            ]
        job_script = os.path.join(self.job_dir, 'job_script.sh')
        with open(job_script, 'w') as f:
            f.writelines("\n".join(lines))


def number_file(file_name, number, max_number, padding= False):
    if number > max_number:
        print("Error: max_number < number")
        return ValueError
    split_file = file_name.split(".")
    file_extension = split_file.pop()
    if padding == True:
        split_file[-1] += '_' + str(number).zfill(len(str(max_number)))
    else:
        split_file[-1] += f'_{number}'

    split_file.append(file_extension)
    file = ".".join(split_file)
    return file

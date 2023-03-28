import datetime
import numpy as np
import os
import write_job_files
import toml
#================================================================================
run_loc = input("running job setup from: (cluster/mac)\n")
if run_loc == "mac":
    # TODO: change home_dir to your username
    home_dir = "/Users/lstaszewski"
elif run_loc == "cluster":
    home_dir = "/home/lstaszewski"
else:
    print("invalid run loc.")
    exit(1)
#================================================================================
# TODO: add a project name and specify the exe as well as its path
project_name = 'template_project_folder'
exe_name = 'code_example.jl'

# setting some paths
project_dir = os.path.join(home_dir, "Research/Projects", project_name)
path_to_exe = os.path.join(project_dir,  exe_name)

#================================================================================
# setting program variables
date = datetime.date.today()

# TODO: specify the job name
job_name = f'{date}.test'

# setting program kwargs
master_config = {

    # TODO: speicify job parameters in groups e.g.
    'hamiltonian' : {
        't1' : 10,
        't2' : [float(x) for x in np.linspace(0, 10, 5)],
    },

    # TODO: add any files need by the exe, the save loc. will be added 
    'files' : {

    },

    # don't remove n_jobs 
    'misc' : {
        'n_jobs' : 0,
        'job_name' : job_name,
        'date': date,
    },
}
#================================================================================
# TODO: specify you directory on the cluster
# setting slurm paths
if run_loc == "mac":
    path_to_job = os.path.join(project_dir, "jobs/waiting", job_name)
elif run_loc == "cluster":
    path_to_job = os.path.join("/data/condmat/lstaszewski", project_name, job_name)
else:
    exit(1)

os.mkdir(path_to_job)
write_job_files.write_toml_files(master_config, path_to_job)

path_to_config = os.path.join(path_to_job, 'config', 'config_$SLURM_ARRAY_TASK_ID.toml')

# get number of jobs from master config
path_to_master_config = os.path.join(path_to_job, 'config/config_master.toml')
with open(path_to_master_config, 'r') as f:
    master_config = toml.load(f)
    n_jobs = master_config["misc"]["n_jobs"]

#================================================================================
# TODO: set the slurm parameters
# setting slurm parameters
slurm_kwargs = {
    'job_name' : job_name,
    'n_jobs' : n_jobs,
    'partition' : "short",
    'time' : "02:00:00",
    'mem' : "2000M",
    'cpus' : 1,
    'mail' : "ALL",
    'modules' : "intel/compiler hdf5 mkl",
    'srun': f"{path_to_exe} {path_to_config}",
}

# TODO: edit relative path to exe if running on mac
run_kwargs = {
    'run' : f"julia {os.path.join('../../../', exe_name)} {os.path.join(path_to_job, 'config', 'config_0.toml')}"
}

if run_loc == "mac":
    write_job_files.write_job_script_mac(run_kwargs, path_to_job)
else:
    write_job_files.write_job_script(slurm_kwargs, path_to_job)

print("finished writing job to:")
print(path_to_job)


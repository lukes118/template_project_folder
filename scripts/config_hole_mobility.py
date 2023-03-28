import datetime
import numpy as np
import os
import write_job_files
import toml
#================================================================================
run_loc = input("running job setup from: (cluster/mac)\n")
if run_loc == "mac":
    home_dir = "/Users/lstaszewski"
elif run_loc == "cluster":
    home_dir = "/home/lstaszewski"
else:
    print("invalid run loc.")
    exit(1)
#================================================================================
project_name = 'julia-ed'
exe_name = 'ed_test.jl'

# setting some paths
project_dir = os.path.join(home_dir, "Research/Projects", project_name)
path_to_exe = os.path.join(project_dir,  exe_name)

#================================================================================
# setting program variables

date = datetime.date.today()
job_name = f'{date}.test'

# setting program kwargs
master_config = {
    'block' : {
        'model' : 'tJ',
        'n_sites' : 10,
    },

    # always need files for saving
    'files' : {

    },

    # don't edit misc
    'misc' : {
        'n_jobs' : 0,
        'job_name' : job_name,
        'date': date,
    },
}

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

run_kwargs = {
    'run' : f"julia {os.path.join('../../../', exe_name)} {os.path.join(path_to_job, 'config', 'config_0.toml')}"
}

if run_loc == "mac":
    write_job_files.write_job_script_mac(run_kwargs, path_to_job)
else:
    write_job_files.write_job_script(slurm_kwargs, path_to_job)

print("finished writing job to:")
print(path_to_job)


from job_class import job
import os
import datetime
import numpy as np

# create job
job_name = f"{datetime.date.today()}.test_job"
my_job = job(job_name, project_name = "template_project_folder")

# set paths
run_loc = input('setting paths for: (mac/cluster) ')
if run_loc == 'mac':
    my_job.set_project_dir(os.path.join(
           "/Users/lstaszewski/Research/Projects", my_job.project_name ,))
    my_job.set_job_dir(os.path.join(
            my_job.project_dir, 'jobs', my_job.job_name,))
    my_job.set_exe(
        os.path.join(my_job.project_dir, "code_example.jl"), 'julia')
else:
    my_job.set_project_dir(os.path.join(
        "/home/lstaszewski/Research/Projects", my_job.project_name ,))
    my_job.set_job_dir(os.path.join(
        "/data/condmat/lstaszewski", my_job.project_name, my_job.job_name,))
    my_job.set_exe(
        os.path.join(my_job.project_dir, "code_example.jl"), 'julia')

# specify the job config n.b numpy arrays will be converted
config = {
    "group_1" : {
        "param_1" : np.linspace(0, 4, 3),
    },
    "group_2" : {
        "param_3" : 10,
    },
    "files" : {
        'save_file' : 'data.h5'
    }
}
my_job.set_config(config)

# specify the slurm variables
slurm_kwargs = {
    'partition' : "short",
    'time' : "02:00:00",
    'mem' : "2000M",
    'cpus' : 1,
    'mail' : "ALL",
    'modules' : "julia",
}
my_job.set_slurm_kwargs(slurm_kwargs)

# write a script that loops through jobs
my_job.write_job_script()
print('finished_writing job to: ')
print(my_job.job_dir)
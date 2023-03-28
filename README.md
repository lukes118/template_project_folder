- add an executable of choice be replacing "code_example.jl"
- go through the /script/config_job.py and replace all the TODO sections

- create a job:
  $ python config_job.py

- job will be created in /jobs/waiting if run on locally
- run with:
  $ bash job_script.sh

- if created on cluster submit with:
  $ sbatch job_script.sh

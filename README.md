minimal example of creating jobs for slurm with python

- edit the test job.py
- set paths and add program args.
- create the job and use job_script.sh to loop through jobs or slurm_script.sh to send as an array job to slurm
- data will be saved in the job folder if a save file is specified e.g. data.h5 (will be renumbered automatically)

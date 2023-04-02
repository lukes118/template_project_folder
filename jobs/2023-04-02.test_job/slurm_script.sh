#!/bin/bash
#SBATCH --partition=short
#SBATCH --time=02:00:00
#SBATCH --mem-per-cpu=2000M
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --job-name=2023-04-02.test_job
#SBATCH --array=0-2
#SBATCH --output=/Users/lstaszewski/Research/Projects/template_project_folder/jobs/2023-04-02.test_job/out/%j.out
#SBATCH --error=/Users/lstaszewski/Research/Projects/template_project_folder/jobs/2023-04-02.test_job/out/%j.err
#SBATCH --mail-type=ALL
set -e
export scratch="/scratch/$USER/$SLURM_JOB_ID"
export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK

mkdir -p $scratch
cd $scratch
module load julia
echo $SLURM_JOB_ID > /Users/lstaszewski/Research/Projects/template_project_folder/jobs/2023-04-02.test_job/out/job_status_$SLURM_ARRAY_TASK_ID.txt
srun julia /Users/lstaszewski/Research/Projects/template_project_folder/code_example.jl /Users/lstaszewski/Research/Projects/template_project_folder/jobs/2023-04-02.test_job/config/config_$SLURM_ARRAY_TASK_ID.toml
echo "done." > /Users/lstaszewski/Research/Projects/template_project_folder/jobs/2023-04-02.test_job/out/job_status_$SLURM_ARRAY_TASK_ID.txt
cd
rm -rf $scratch
exit 0
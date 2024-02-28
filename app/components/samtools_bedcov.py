import subprocess

# Function to execute samtools depth
def run_samtools_bedcov(bam_path, bed_path, depth_path):
    command = f"awk '{{sub(/^chr/, \"\", $1); print}}' '{bed_path}' | samtools bedcov -b - '{bam_path}' > '{depth_path}'"
    subprocess.run(command, shell=True)
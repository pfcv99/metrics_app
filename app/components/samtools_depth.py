import subprocess

# Function to execute samtools depth
def run_samtools_depth(bam_path, bed_path, depth_path):
    command = f"awk '{{sub(/^chr/, \"\", $1); print}}' '{bed_path}' | samtools depth -b - '{bam_path}' > '{depth_path}'"
    subprocess.run(command, shell=True)


def run_samtools_depth2(bam_path, bed_path, depth_path):
    command = f"samtools depth -b {bed_path} {bam_path} > {depth_path}"
    subprocess.run(command, shell=True)
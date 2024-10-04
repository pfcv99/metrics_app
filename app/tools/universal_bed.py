import argparse
import json
import re


def load_gene_mapping(mapping_file):
    with open(mapping_file, 'r') as json_file:
        return json.load(json_file)


def process_bed_file(input_file, output_file, mapping_file, remove_chr_prefix=False):
    # Load the gene mapping from JSON
    gene_mapping = load_gene_mapping(mapping_file)

    # Dictionary to keep track of exon count based on strand
    exon_counts = {}

    with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
        for line in infile:
            fields = line.strip().split('\t')

            # Skip header lines if present
            if fields[1] == 'chromStart' or not fields[1].isdigit():
                continue

            # Extract information from column 4 using regex
            match = re.match(r'(ENST\d+\.\d+)_exon_\d+_\d+_chr.+_\d+_([fr])', fields[3])
            if not match:
                continue

            transcript_id = match.group(1)
            strand = '+' if match.group(2) == 'f' else '-'

            # Get gene information from mapping
            gene_name = gene_mapping.get(transcript_id, {}).get('Gene name', 'Unknown')

            # Create a unique identifier for the gene-strand combination
            gene_strand_key = (gene_name, strand)

            # Update exon count based on gene-strand
            if gene_strand_key not in exon_counts:
                exon_counts[gene_strand_key] = 1 if strand == '+' else 0
            else:
                if strand == '+':
                    exon_counts[gene_strand_key] += 1
                else:
                    exon_counts[gene_strand_key] -= 1

            exon_count = exon_counts[gene_strand_key]

            # Calculate the difference between columns 3 and 2
            start = int(fields[1])
            end = int(fields[2])
            diff = end - start

            # Remove the "chr" prefix from the chromosome number if needed
            chromosome = fields[0]
            if remove_chr_prefix:
                chromosome = chromosome[3:] if chromosome.startswith("chr") else chromosome

            # Write to the output file
            outfile.write(f"{chromosome}	{fields[1]}	{fields[2]}	{gene_name}	{exon_count}	{diff}	{strand}\n")


def main():
    parser = argparse.ArgumentParser(description="Process a BED file and optionally remove 'chr' prefix from chromosome numbers.")

    parser.add_argument('input_file', help="Path to the input BED file.")
    parser.add_argument('output_file', help="Path to the output BED file.")
    parser.add_argument('mapping_file', help="Path to the gene-transcript mapping JSON file.")
    parser.add_argument('--remove-chr-prefix', action='store_true',
                        help="Remove 'chr' prefix from chromosome names.")

    args = parser.parse_args()

    process_bed_file(args.input_file, args.output_file, args.mapping_file, args.remove_chr_prefix)


if __name__ == "__main__":
    main()
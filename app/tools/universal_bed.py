import argparse
import json
import csv
import re


def load_gene_mapping(mapping_file):
    with open(mapping_file, 'r') as json_file:
        return json.load(json_file)


def load_mane_mapping(mane_csv):
    mane_mapping = {}
    with open(mane_csv, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            gene_name = row['Gene']
            grch37_id = row['Ensembl StableID GRCh37 (Not MANE)']
            if grch37_id != '':
                mane_mapping[grch37_id] = gene_name
    return mane_mapping


def process_bed_file(input_files, output_file, genome_version, mapping_file=None, mane_file=None, add_chr_prefix=False):
    # Load gene mapping from JSON if provided
    gene_mapping = load_gene_mapping(mapping_file) if mapping_file else {}
    # Load MANE mapping if provided
    mane_mapping = load_mane_mapping(mane_file) if mane_file else {}

    exon_counts = {}
    rows = []

    for input_file in input_files:
        with open(input_file, 'r') as infile:
            bed_data = json.load(infile)
            for record in bed_data:
                chromosome = record['chromosome']
                start = record['start']
                end = record['end']
                gene_id = record['gene_stable_id']
                gene_name = record.get('gene_name', '')
                exon_id = record['exon_id']
                strand = record['strand']
                transcript_id = record['transcript_id']

                # Only include standard chromosomes (1-22, X, Y)
                if not re.match(r'^(\d+|X|Y)$', chromosome):
                    continue

                # Determine gene name, fallback to gene stable ID if empty
                if not gene_name:
                    gene_name = gene_id

                # Apply MANE filtering for hg37
                if genome_version == 'hg37' and mane_mapping and transcript_id not in mane_mapping:
                    continue
                elif genome_version == 'hg37' and transcript_id in mane_mapping:
                    gene_name = mane_mapping[transcript_id]

                # Add 'chr' prefix if needed
                if add_chr_prefix:
                    chromosome = f'chr{chromosome}'

                # Collect row
                rows.append((chromosome, int(start), int(end), gene_name, strand))

    # Sort rows by exon start and chromosome
    rows.sort(key=lambda x: (x[0], x[1]))

    # Recalculate exon numbers based on strand for hg37
    exon_counts = {}
    updated_rows = []
    for chromosome, start, end, gene_name, strand in rows:
        gene_strand_key = (gene_name, strand)

        if gene_strand_key not in exon_counts:
            exon_counts[gene_strand_key] = []
        exon_counts[gene_strand_key].append((chromosome, start, end, gene_name, strand))

    # Assign exon numbers
    for (gene_name, strand), exon_list in exon_counts.items():
        if strand == '1':
            for exon_number, (chromosome, start, end, gene_name, strand) in enumerate(exon_list, start=1):
                exon_length = end - start
                updated_rows.append((chromosome, start, end, gene_name, exon_number, exon_length, strand))
        else:
            for exon_number, (chromosome, start, end, gene_name, strand) in enumerate(exon_list, start=1):
                exon_length = end - start
                updated_rows.append((chromosome, start, end, gene_name, len(exon_list) - exon_number + 1, exon_length, strand))

    rows = updated_rows

    # Write to output file
    with open(output_file, 'w') as outfile:
        for row in rows:
            outfile.write(f"{row[0]}	{row[1]}	{row[2]}	{row[3]}	{row[4]}	{row[5]}	{row[6]}\n")


def main():
    parser = argparse.ArgumentParser(description="Process BED files in JSON format, join MANE data, and optionally add 'chr' prefix.")

    parser.add_argument('input_files', nargs='+', help="Path(s) to the input BED JSON file(s). For hg38 provide both Select and Plus Clinical.")
    parser.add_argument('output_file', help="Path to the output BED file.")
    parser.add_argument('--genome-version', choices=['hg37', 'hg38'], required=True, help="Genome version: hg37 or hg38.")
    parser.add_argument('--mapping-file', help="Path to the gene-transcript mapping JSON file.")
    parser.add_argument('--mane-file', help="Path to the MANE GRCh37 mapping CSV file.")
    parser.add_argument('--add-chr-prefix', action='store_true', help="Add 'chr' prefix to chromosome names.")

    args = parser.parse_args()

    process_bed_file(
        args.input_files,
        args.output_file,
        args.genome_version,
        args.mapping_file,
        args.mane_file,
        args.add_chr_prefix
    )


if __name__ == "__main__":
    main()
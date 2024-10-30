import argparse
import json
import re

def load_mane_mapping(mane_json):
    mane_mapping = {}
    with open(mane_json, 'r') as json_file:
        mane_data = json.load(json_file)
        for record in mane_data:
            refseq_id = record.get('refseq').split('.')[0]
            transcript_id = record.get('transcript_id', '').split('.')[0]  # Adicionado para obter o transcript_id
            gene_name = record.get('gene_name', '')
            if refseq_id:
                mane_mapping[refseq_id] = gene_name
            if transcript_id:
                mane_mapping[transcript_id] = gene_name  # Armazena também o transcript_id no mapeamento
    return mane_mapping

def process_bed_file(input_files, output_file, genome_version, mane_file=None, add_chr_prefix=False):
    # Load MANE mapping from JSON if provided
    mane_mapping = load_mane_mapping(mane_file) if mane_file else {}

    rows = []

    for input_file in input_files:
        with open(input_file, 'r') as infile:
            bed_data = json.load(infile)
            for record in bed_data:
                chromosome = record.get('chromosome')
                start = record.get('start')
                end = record.get('end')
                gene_id = record.get('gene_stable_id')
                gene_name = record.get('gene_name', '')
                strand = record.get('strand')
                refseq_id = record.get('refseq', '').split('.')[0]  # Get the RefSeq ID
                transcript_id = record.get('transcript_id', '').split('.')[0]  # Get the Transcript ID

                # Only include standard chromosomes (1-22, X, Y)
                if not re.match(r'^(\d+|X|Y)$', chromosome):
                    continue

                # Determine gene name, fallback to stable gene ID if empty
                if not gene_name:
                    gene_name = gene_id

                # Apply MANE filtering for hg37 and hg38 based on refseq_id or transcript_id matching
                if genome_version in ['hg37', 'hg38']:
                    if refseq_id in mane_mapping:
                        gene_name = mane_mapping[refseq_id]
                    elif transcript_id in mane_mapping:
                        gene_name = mane_mapping[transcript_id]
                    else:
                        continue  # Skip if neither refseq_id nor transcript_id is found

                # Add 'chr' prefix if needed
                if add_chr_prefix:
                    chromosome = f'chr{chromosome}'

                # Collect row
                rows.append((chromosome, int(start), int(end), gene_name, strand))

    # Sort rows by exon start and chromosome
    rows.sort(key=lambda x: (x[0], x[1]))

    # Recalculate exon numbers based on strand for hg37 and hg38
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
            total_exons = len(exon_list)
            for exon_number, (chromosome, start, end, gene_name, strand) in enumerate(exon_list, start=1):
                exon_length = end - start
                updated_rows.append((chromosome, start, end, gene_name, total_exons - exon_number + 1, exon_length, strand))

    # Write the output
    with open(output_file, 'w') as outfile:
        for row in updated_rows:
            outfile.write('\t'.join(map(str, row)) + '\n')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Process BED files with gene mapping.")
    parser.add_argument('input_files', nargs='+', help='Input BED files in JSON format.')
    parser.add_argument('output_file', help='Output file for processed data.')
    parser.add_argument('genome_version', choices=['hg37', 'hg38'], help='Genome version to use.')
    parser.add_argument('--mane_file', required=True, help='MANE mapping file in JSON format.')
    parser.add_argument('--add_chr_prefix', action='store_true', help='Add "chr" prefix to chromosomes.')

    args = parser.parse_args()
    process_bed_file(args.input_files, args.output_file, args.genome_version, args.mane_file, args.add_chr_prefix)

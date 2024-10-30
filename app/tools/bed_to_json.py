import json
import argparse

def load_refseq_data(refseq_file):
    refseq_data = {}
    with open(refseq_file, 'r') as infile:
        refseq_records = json.load(infile)
        for record in refseq_records:
            transcript_id = record.get("Transcript stable ID version")
            refseq = record.get("RefSeq")
            gene_name = record.get("Gene name")
            if transcript_id:
                refseq_data[transcript_id] = {
                    "refseq": refseq,
                    "gene_name": gene_name
                }
    return refseq_data

def bed_to_json(input_file, output_file, refseq_file=None):
    bed_records = []
    refseq_data = load_refseq_data(refseq_file) if refseq_file else {}

    with open(input_file, 'r') as infile:
        # Ignore the first header line
        header = infile.readline()

        for line in infile:
            # Ignore additional header lines or empty lines
            if line.startswith("#") or line.strip() == "":
                continue

            fields = line.strip().split('\t')
            
            # Adjust according to the expected BED format (8 columns)
            if len(fields) >= 8:
                chromosome = fields[0]
                start = int(fields[1])
                end = int(fields[2])
                gene_stable_id = fields[3]
                gene_name = fields[4]
                exon_id = fields[5]
                strand = fields[6]
                transcript_id = fields[7]

                # Check if there is RefSeq information
                refseq_info = refseq_data.get(transcript_id)
                refseq = refseq_info["refseq"].split('.')[0] if refseq_info else None

                # Add the record only if the RefSeq is available
                if refseq is not None:
                    bed_records.append({
                        "chromosome": chromosome,
                        "start": start,
                        "end": end,
                        "gene_stable_id": gene_stable_id,
                        "gene_name": gene_name,
                        "exon_id": exon_id,
                        "strand": strand,
                        "transcript_id": transcript_id,
                        "refseq": refseq  # Optional field
                    })

    with open(output_file, 'w') as jsonfile:
        json.dump(bed_records, jsonfile, indent=4)

def main():
    parser = argparse.ArgumentParser(description="Convert a BED file to JSON.")
    parser.add_argument('input_file', help="Path to the input BED file.")
    parser.add_argument('output_file', help="Path to the output JSON file.")
    parser.add_argument('--refseq_file', help="Path to the auxiliary JSON file with RefSeq data.", required=False)
    args = parser.parse_args()

    bed_to_json(args.input_file, args.output_file, args.refseq_file)

if __name__ == "__main__":
    main()

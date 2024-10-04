import argparse
import json

def create_json_from_txt(txt_file, json_file):
    mapping = {}

    with open(txt_file, 'r') as infile:
        # Skip the header line
        next(infile)

        for line in infile:
            fields = line.strip().split('\t')
            gene_id = fields[0]
            transcript_id = fields[1] if len(fields) > 1 else None
            gene_name = fields[2] if len(fields) > 2 and fields[2] else gene_id

            if transcript_id:
                # Add data to the mapping
                mapping[transcript_id] = {
                    "Gene stable ID version": gene_id,
                    "Gene name": gene_name
                }

    # Write the mapping to a JSON file
    with open(json_file, 'w') as outfile:
        json.dump(mapping, outfile, indent=4)

def main():
    parser = argparse.ArgumentParser(description="Convert a TXT file to a JSON file containing gene-transcript mappings.")
    parser.add_argument('txt_file', help="Path to the input TXT file.")
    parser.add_argument('json_file', help="Path to the output JSON file.")
    args = parser.parse_args()

    create_json_from_txt(args.txt_file, args.json_file)

if __name__ == "__main__":
    main()
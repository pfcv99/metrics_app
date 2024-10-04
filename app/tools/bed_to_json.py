import json
import argparse

def bed_to_json(input_file, output_file):
    bed_records = []

    with open(input_file, 'r') as infile:
        # Ignorar a primeira linha do cabeçalho
        header = infile.readline()

        for line in infile:
            # Ignorar linhas de cabeçalho adicionais ou linhas vazias
            if line.startswith("#") or line.strip() == "":
                continue

            fields = line.strip().split('\t')
            
            # Ajustar conforme o formato esperado da BED (neste caso 8 colunas)
            if len(fields) >= 8:
                chromosome = fields[0]
                start = int(fields[1])
                end = int(fields[2])
                gene_stable_id = fields[3]
                gene_name = fields[4]
                exon_id = fields[5]
                strand = fields[6]
                transcript_id = fields[7]

                bed_records.append({
                    "chromosome": chromosome,
                    "start": start,
                    "end": end,
                    "gene_stable_id": gene_stable_id,
                    "gene_name": gene_name,
                    "exon_id": exon_id,
                    "strand": strand,
                    "transcript_id": transcript_id
                })

    with open(output_file, 'w') as jsonfile:
        json.dump(bed_records, jsonfile, indent=4)

def main():
    parser = argparse.ArgumentParser(description="Converte um ficheiro BED para JSON.")
    parser.add_argument('input_file', help="Caminho para o ficheiro BED de input.")
    parser.add_argument('output_file', help="Caminho para o ficheiro JSON de output.")
    args = parser.parse_args()

    bed_to_json(args.input_file, args.output_file)

if __name__ == "__main__":
    main()

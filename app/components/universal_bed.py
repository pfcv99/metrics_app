def process_bed_file(input_file, output_file, remove_chr_prefix=False):
    last_gene = None
    exon_count = 0
    
    with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
        for line in infile:
            fields = line.strip().split('\t')
            
            # Dividindo a coluna 4 pelo separador ','
            gene_info = fields[3].split(',')
            gene = gene_info[0]
            
            # Verificando se o gene mudou para contar os exons
            if gene != last_gene:
                exon_count = 1
            else:
                exon_count += 1
            
            # Calculando a diferença entre $3 e $2
            start = int(fields[1])
            end = int(fields[2])
            diff = end - start
            
            # Remove o prefixo "chr" do número do cromossomo se necessário
            chromosome = fields[0]
            if remove_chr_prefix:
                chromosome = chromosome[3:] if chromosome.startswith("chr") else chromosome
            
            # Atualizando a última gene
            last_gene = gene
            
            # Escrevendo no arquivo de saída
            outfile.write(f"{chromosome}\t{fields[1]}\t{fields[2]}\t{gene}\t{exon_count}\t{diff}\n")

# Exemplo de uso com a opção de remover o prefixo "chr"
input_file = 'data/regions/genome_exons/hg19_Twist_ILMN_Exome_2.0_Plus_Panel_annotated.BED'
output_file_with_chr = 'data/regions/genome_exons/hg19_Twist_ILMN_Exome_2.0_Plus_Panel_annotated_modif.bed'
output_file_no_chr = 'data/regions/genome_exons/hg19_Twist_ILMN_Exome_2.0_Plus_Panel_annotated_modif_nochr.bed'

# Chamar a função com e sem a remoção do prefixo "chr"
process_bed_file(input_file, output_file_with_chr, remove_chr_prefix=False)
process_bed_file(input_file, output_file_no_chr, remove_chr_prefix=True)


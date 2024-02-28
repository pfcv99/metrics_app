from components import samtools_depth

samtools_depth.run_samtools_depth("data/mapped/1106179.bam", "data/regions/gene_panels/Oncorisk_(96 genes).bed", "data/depth/testsamtools.depth")
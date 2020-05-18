# METS
METS(Multi-Satellite Extractor for Targeted Sequencing) is an accurate tool for large-scale Multi-Satellite extracting for targeted sequencing data.

Copyright Holder: Wang Fengge, Huo Yongxue  
email: admin@plantdna.cn

# Program Requirement
Running METS requires a GNU-like environment. It should be possible to
      run METS on a Linux or Mac OS, Ubuntu Server 18.04 is recommended.

METS requires the following external tools:

1. bamtools　　
2. blast tool suite
3. bwa　
4. fastx_toolkit
5. picard　
6. samtools
7. seqtk

  Seven tools maybe the seven demigods in the book "The Heroes of Olympus" by Rick Riordan

# Configuration
  Please config the tools in the profile first. An example is the file under subtools named profiles-maizedna-1.sh

# Running
	./METS.sh SCRIPT_DIR ENV_FILE METHOD

  METS.sh takes 3 parmeters:

1. SCRIPT_DIR: the folder which the METS.sh located            
2. ENV_FILE: the configuration file        
3. METHOD:  to specify the algorithm: precise or broad

	please check the launch.sh to find the usage details.

* Format of reference fasta file

	It is a standard fasta file, which holds the locus name and sequence information.

* Format of reference stat information:
```
#ID	SSR.No	Motif_len	Motif	Repeat_times	Start	End	Repeat_len	Seq_len
s258878	1	3	GCT	5	301	315	15	615
s282049	1	3	TGG	5	301	315	15	615
s282991	1	3	TGT	5	301	315	15	615
```

This file show the detail information of the references.

* Output files

1. Variants for all loci of each sample
   working/04_reads/SAMPLE_NAME.site.stat
```
#Site   Motif   Repeat_len      Reads_num       Total_reads     Proportion
s258878 GCT     3       16      2350    0.0068085106383
s258878 GCT     6       1085    2350    0.46170212766
s258878 GCT     9       1249    2350    0.531489361702
```		 

   This file shows result of all variants for each locus of a sample.



2. Variants for each locus of each sample
   working/04_reads/SAMPLE_NAME/LOCUS_NAME/LOCUS_NAME.ssr.stat

```
#Site   Motif   Repeat_len      Reads_num       Total_reads     Proportion
s258878 GCT     3       16      2350    0.0068085106383
s258878 GCT     6       1085    2350    0.46170212766
s258878 GCT     9       1249    2350    0.531489361702
```

3. Reads for each variants of each locus of each sample
working/04_reads/SAMPLE_NAME/LOCUS_NAME/SSRn.fas
Standard fasta file, grouped all reads corresponding a variants of a locus of a sample.

example as:
```
>CRC8E:03524:00917
GATCTGTTTGCCAGCTGGGGCAAGATTTCTTCGGTGCCTGCACCCTTTCTCTTGCGGTTGTTTATGCTATCGCTGCTGCTGATTGTGGGGTTCCTGCGTTCGCCACTGTGACTGTCACTTTGCTGGTGCTGTTCCTGGTTGCATCTGCTTTTCAGTATGTGGGGCTTGAGCTTGTTC
>CRC8E:03306:03509
TAACTGTGCCTTGATCTGTTTGCCAGCTGGGGCAAGATTTCTTCGGTGCCTGCACCCTTTCTCTTGCGGTTGTTTATGCTATCGCTGCTGCTGATTGTGGGGTTCCTGCGTTCGCCACTGTGACTGTCACTTTGCTGGTGCTGTTCCTGGTTGCATCTGCTTTTCAGTATGTGGGGCTTGAGCTTGTTC
>CRC8E:04520:05520
GATCTGTTTGCCAGCTGGGGCAAGATTTCTTCGGTGCCTGCACCCTTTCTCTTGCGGTTGTTTATGCTATCGCTGCTGCTGATTGTGGGGTTCCTGCGTTCGCCACTGTGACTGTCACTTTGCTGGTGCTGTTCCTGGTTGCATCTGCTTTTCAGTATGTGGGGCTTGAGCTTGTTC
```

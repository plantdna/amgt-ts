#!/bin/bash
mkdir -p $PROJECT_DIR/00_fastq
mkdir -p $PROJECT_DIR/01_assembly
mkdir -p $PROJECT_DIR/02_site
mkdir -p $PROJECT_DIR/03_blast
mkdir -p $PROJECT_DIR/04_reads

############################################## Part1 Aseembly ###################################################
##
mkdir -p $PROJECT_DIR/00_fastq/clean
find -L $PROJECT_DIR/00_fastq -name "*.$FORMAT" -print | \
    xargs -n 1 -P 4 -I PREFIX \
    sh -c '
        sample=`basename PREFIX | cut -f 1 -d "."`
        lane_id=${sample}
        echo "[`date`]: Start processing ${sample} ... "

        $FASTX_DIR/fastq_quality_filter -q $QUALITY_FILTER -p 80 -Q 33 \
            -i PREFIX | $FASTX_DIR/fastx_clipper -l 100 -Q 33 -i - \
                    -o $PROJECT_DIR/00_fastq/clean/${sample}.clean.fq
        '

find -L $PROJECT_DIR/00_fastq/clean -name "*.clean.fq" -print | \
    xargs -n 1 -P 4 -I PREFIX \
    sh -c '
        sample=`basename PREFIX | cut -f 1 -d "."`
        lane_id=${sample}
        echo "[`date`]: Start processing ${sample} ... "

        $BWA mem -t $CPU_CORES -M -R "@RG\tID:${lane_id}\tLB:${sample}\tPL:IonTo\tPU:${sample}\tSM:${sample}" \
            $REF_FILE $PROJECT_DIR/00_fastq/clean/${sample}.clean.fq \
            > $PROJECT_DIR/01_assembly/${sample}.bwa.sam \
            2> $PROJECT_DIR/01_assembly/${sample}.bwa.log
        ## sort bam file
        java -Djava.io.tmpdir=$TMP_DIR -jar $PICARD SortSam \
            I=$PROJECT_DIR/01_assembly/${sample}.bwa.sam \
            O=$PROJECT_DIR/01_assembly/${sample}.bwa.sort.bam \
            SORT_ORDER=coordinate \
            >> $PROJECT_DIR/01_assembly/${sample}.bwa.log 2>&1 && \
            rm -v $PROJECT_DIR/01_assembly/${sample}.bwa.sam
        $SAMTOOLS index $PROJECT_DIR/01_assembly/${sample}.bwa.sort.bam
    '

########################################## Part2 split sites ###########################################
find $PROJECT_DIR/01_assembly -name "*.bam" -print | \
    xargs -n 1 -P 5 -I PREFIX \
    sh -c '
        sample=`basename PREFIX | cut -d"." -f1`

        echo "[`date`]: Start processing ${sample} ... "

        #forward strand 30''
        $SAMTOOLS view -F 20 $PROJECT_DIR/01_assembly/${sample}.bwa.sort.bam | \
            $SAMTOOLS view -bt $REF_FILE.fai - \
            > $PROJECT_DIR/01_assembly/${sample}.bwa.sort.fs.bam

        #reverse strand 30''
        $SAMTOOLS view -f 0x10 $PROJECT_DIR/01_assembly/${sample}.bwa.sort.bam | \
            $SAMTOOLS view -bt $REF_FILE.fai - \
            > $PROJECT_DIR/01_assembly/${sample}.bwa.sort.rs.bam

        #index
        $BAMTOOLS index -in $PROJECT_DIR/01_assembly/${sample}.bwa.sort.fs.bam
        $BAMTOOLS index -in $PROJECT_DIR/01_assembly/${sample}.bwa.sort.rs.bam
    '


#bam2fas
for file in `ls $PROJECT_DIR/01_assembly/*sort.bam`
do
    echo "processing ${file}"
    sample=`basename ${file} | cut -d"." -f1`
    mkdir -p $PROJECT_DIR/02_site/${sample}
    for site in `awk '!/^#/ {print $1}' $POS_FILE | uniq`;
    do
        $BAMTOOLS convert -format fasta -region ${site} \
            -in $PROJECT_DIR/01_assembly/${sample}.bwa.sort.fs.bam \
            > $PROJECT_DIR/02_site/${sample}/${site}.bwa.sort.fs.fasta
        $BAMTOOLS convert -format fasta -region ${site} \
            -in $PROJECT_DIR/01_assembly/${sample}.bwa.sort.rs.bam \
            > $PROJECT_DIR/02_site/${sample}/${site}.bwa.sort.rs.fasta
        $SEQTK seq -r \
            $PROJECT_DIR/02_site/${sample}/${site}.bwa.sort.rs.fasta | \
            cat $REF_DIR/site/${site}.fa \
                $PROJECT_DIR/02_site/${sample}/${site}.bwa.sort.fs.fasta - \
                > $PROJECT_DIR/02_site/${sample}/${site}.bwa.sort.fasta
    done
done

############################################### Part3 find SSR sequence and repeat times############################################
## 1 blast and filt
for file in `ls $PROJECT_DIR/01_assembly/*sort.bam`
do
    sample=`basename ${file} | cut -d"." -f1`
    echo "[`date`]: Start processing ${sample} ... "
    mkdir -p $PROJECT_DIR/03_blast/${sample}/
    for site in `awk '!/^#/ {print $1}' $POS_FILE | uniq`;
    do
        $BLAST_BIN/makeblastdb -in $PROJECT_DIR/02_site/${sample}/${site}.bwa.sort.fasta -dbtype nucl \
            -out $PROJECT_DIR/02_site/${sample}/${site}.bwa.sort.realn \
            -logfile $PROJECT_DIR/02_site/${sample}/${site}.bwa.sort.fasta.log

        $BLAST_BIN/blastn -query $REF_DIR/flank/left/${site}.lf.fas \
            -db  $PROJECT_DIR/02_site/${sample}/${site}.bwa.sort.realn \
            -task blastn -evalue 10 -num_threads 10 -max_target_seqs 10000 \
            -outfmt '7 qseqid qlen sseqid slen pident length mismatch gapopen qstart qend qcovs sstart send evalue bitscore' \
            -out $PROJECT_DIR/03_blast/${sample}/${site}.bwa.sort.fasta.lf.blastn
        awk '!a[$2 $3]++' $PROJECT_DIR/03_blast/${sample}/${site}.bwa.sort.fasta.lf.blastn \
            > $PROJECT_DIR/03_blast/${sample}/${site}.bwa.sort.fasta.lf.blastn.flt

        $BLAST_BIN/blastn -query $REF_DIR/flank/right/${site}.rf.fas \
            -db  $PROJECT_DIR/02_site/${sample}/${site}.bwa.sort.realn \
            -task blastn -evalue 10 -num_threads 10 -max_target_seqs 10000 \
            -outfmt '7 qseqid qlen sseqid slen pident length mismatch gapopen qstart qend qcovs sstart send evalue bitscore' \
            -out $PROJECT_DIR/03_blast/${sample}/${site}.bwa.sort.fasta.rf.blastn

        awk '!a[$2 $3]++' $PROJECT_DIR/03_blast/${sample}/${site}.bwa.sort.fasta.rf.blastn \
            > $PROJECT_DIR/03_blast/${sample}/${site}.bwa.sort.fasta.rf.blastn.flt
    done
done
###############################################################
##
## 2 find different repeat times of SSR-motif
##

for file in `ls $PROJECT_DIR/01_assembly/*sort.bam`
do
    sample=`basename ${file} | cut -d"." -f1`

    echo "[`date`]: Start processing ${sample} ... "

    for site in `awk '!/^#/ {print $1}' $POS_FILE | uniq`;
    do
        python $SCRIPT_DIR/subtools/ssr/precise/processBlast.py \
          -l $PROJECT_DIR/03_blast/${sample}/${site}.bwa.sort.fasta.lf.blastn.flt \
          -r $PROJECT_DIR/03_blast/${sample}/${site}.bwa.sort.fasta.rf.blastn.flt \
          -o $PROJECT_DIR/03_blast/${sample}/${site}.bwa.sort.fasta.blastn.flt.bed


        python $SCRIPT_DIR/subtools/ssr/precise/generateSeq.py \
          -b $PROJECT_DIR/02_site/${sample}/${site}.bwa.sort.fasta \
          -s $PROJECT_DIR/03_blast/${sample}/${site}.bwa.sort.fasta.blastn.flt.bed \
          -o $PROJECT_DIR/03_blast/${sample}/${site}.bwa.sort.fasta.blastn.flt.fas

        python $SCRIPT_DIR/subtools/ssr/precise/ssrFinder.py \
          -l ${site} \
          -f $PROJECT_DIR/02_site/${sample}/${site}.bwa.sort.fasta \
          -m $POS_FILE \
          -r $PROJECT_DIR/03_blast/${sample}/${site}.bwa.sort.fasta.blastn.flt.fas \
          -o $PROJECT_DIR/04_reads/${sample}/${site}

    done
done

###############################################################
## 3 merge stats files
for file in `ls $PROJECT_DIR/01_assembly/*sort.bam`
do
    sample=`basename ${file} | cut -d"." -f1`
    echo "[`date`]: Start processing ${sample} ... "

    cat $PROJECT_DIR/04_reads/${sample}/*/*.ssr.stat | awk ' !x[$0]++' | sort -k1.2n \
       > $PROJECT_DIR/04_reads/${sample}.site.stat
done

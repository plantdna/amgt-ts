#!/bin/bash
mkdir -p $PROJECT_DIR/00_fastq/
mkdir -p $PROJECT_DIR/01_assembly
mkdir -p $PROJECT_DIR/04_reads

############################################## Part1 Aseembly ###################################################

mkdir -p $PROJECT_DIR/00_fastq/clean
find -L $PROJECT_DIR/00_fastq -name "*.$FORMAT" -print | \
    xargs -n 1 -P 4 -I PREFIX \
    sh -c '
        sample=`basename PREFIX | cut -f 1 -d "."`
        lane_id=${sample}
        echo "[`date`]: Start processing ${sample} ... "

        $FASTX_DIR/fastq_quality_filter -q $QUALITY_FILTER -p 80 -Q 33 \
            -i PREFIX  \
                    -o $PROJECT_DIR/00_fastq/clean/${sample}.clean.fq
        '


##
## bwa-mem mapping and GATK realignment
##
find -L $PROJECT_DIR/00_fastq/clean -name "*.clean.fq" -print | \
    xargs -n 1 -P 4 -I PREFIX \
    sh -c '
        sample=`basename PREFIX | cut -f 1 -d "."`
        lane_id=${sample}
        echo "[`date`]: Start processing ${sample} ... "

        $BWA mem -t 6 -M -R "@RG\tID:${lane_id}\tLB:${sample}\tPL:IonTo\tPU:${sample}\tSM:${sample}" \
            $REF_FILE PREFIX \
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
########################################### Part2 SSR finder #################################################
#get SSR repeats from bam files.
find $PROJECT_DIR/01_assembly -name "*.bam" -print | \
    xargs -n 1 -P 5 -I PREFIX \
    sh -c '
        sample=`basename PREFIX | cut -d"." -f1`
        echo "[`date`]: Start processing ${sample} ......"
        mkdir -p $PROJECT_DIR/04_reads/${sample}

        $SAMTOOLS view PREFIX | \
            python $SCRIPT_DIR/subtools/ssr/broad/processBam.py -i - \
                -p $POS_FILE \
                -r $REF_FILE \
                -o $PROJECT_DIR/04_reads/${sample}
    '
for file in `ls $PROJECT_DIR/01_assembly/*.bam`;
do
    sample=`basename ${file} | cut -d"." -f1`
    echo "[`date`]: Start processing ${sample} ... "

    cat $PROJECT_DIR/04_reads/${sample}/*/*.ssr.stat | awk ' !x[$0]++' | sort -k1.2n \
       > $PROJECT_DIR/04_reads/${sample}.site.stat
done

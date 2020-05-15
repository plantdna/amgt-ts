# !/bin/bash
export BASE_DIR=/mnt/diskc/gitlab/mets
export REF_DIR=$BASE_DIR/ref
export SCRIPT_DIR=$BASE_DIR
export PROJECT_DIR=$BASE_DIR/working
export TMP_DIR=$BASE_DIR/tmp
export TOOLS_DIR=/mnt/diskc/gitlab/s2s/tools

export FORMAT=fq

export PICARD=$TOOLS_DIR/picard.jar
export BWA=$TOOLS_DIR/bwa-0.7.17/bwa
export SAMTOOLS=$TOOLS_DIR/samtools/bin/samtools
export BAMTOOLS=$TOOLS_DIR/bamtools/bin/bin/bamtools
export SEQTK=$TOOLS_DIR/seqtk-1.2/seqtk

# fastx
export FASTX_DIR=$TOOLS_DIR/fastx_toolkit_0.0.13

# blast
export BLAST_BIN=/mnt/diskc/ampseq-ssr/ncbi-blast-2.6.0+/bin

export REF_FILE=$REF_DIR/sites.amplicon.fa
export POS_FILE=$REF_DIR/sites.motif.info.stats

# parameters
export CPU_CORES=2
export QUALITY_FILTER=20

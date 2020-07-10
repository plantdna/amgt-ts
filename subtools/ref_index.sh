#!/bin/bash

export REF_PREFIX=`echo $REF_FILE | perl -pe 's/\.[a-zA-Z]+?$//;'`

## 1 index ref file
# bwa and samtools index
$BWA index $REF_FILE
$SAMTOOLS faidx $REF_FILE

## 2 separate each site
python $SCRIPT_DIR/subtools/ref/splitRef.py $SCRIPT_DIR/ref $REF_FILE

## 3 split flanking sequence (20bp)
python $SCRIPT_DIR/subtools/ref/splitFlankSeq.py $FLANK_LENGTH $REF_FILE $POS_FILE

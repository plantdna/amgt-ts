import csv

def getRefData(refSeq, refStat):
    ref_stat_file=refStat
    ref_sequence_file=refSeq

    ref_stat_reader = csv.DictReader(open(ref_stat_file), delimiter="\t")
    ref_sequence_reader = open(ref_sequence_file)

    # When we talk about hash tables, we're actually talking about dictionary.
    ref_stat_data = {}
    ref_sequence_data = {}

    # P06     1       4       GTAT    4       50      66      16      211
    # P07     1       2       AT      4       56      64      8       217
    # P07     2       4       AAAC    4       152     168     16      217

    for row in ref_stat_reader:
        if ref_stat_data.get(row["#ID"], None) == None: # the first motif
            ref_stat_data[row["#ID"]] = [ {"locus": row["#ID"], "motif": row["Motif"], "ssr_pos_left": int(row["Start"]),
                        "ssr_pos_right": int(row["End"]), "motif_length":int(row["Motif_len"]),
                                          "repeat_times": int(row["Repeat_times"])}]
        else: # more motif
            ref_stat_data[row["#ID"]].append({"locus": row["#ID"], "motif": row["Motif"], "ssr_pos_left": int(row["Start"]),
                        "ssr_pos_right": int(row["End"]), "motif_length":int(row["Motif_len"]),
                                          "repeat_times": int(row["Repeat_times"])})

    # end for

    contig_tmp = ''
    line = ref_sequence_reader.readline()
    lineIndex = 0
    while line:
        lineIndex = lineIndex+ 1
        if lineIndex % 2 == 1:
            contig_tmp = line
        else:
            ref_sequence_data[contig_tmp.rstrip('\n').lstrip('>')] = line.rstrip('\n')
        # end if

        line = ref_sequence_reader.readline()
    # end while

    ref_sequence_reader.close()
    return ref_stat_data, ref_sequence_data

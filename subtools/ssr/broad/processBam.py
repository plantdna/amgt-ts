import csv
import isSsrRegionCovered
import cigarResolved
import prepareRef
import argparse

import sys
import os, os.path
import errno

OUTPUT_DIR="output/"

# Taken from https://stackoverflow.com/a/600612/119527
def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc: # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else: raise

def safe_open_w(path):
    ''' Open "path" for writing, creating any parent directories as needed.
    '''
    mkdir_p(os.path.dirname(path))
    return open(path, 'w')
# end def

def dumpReads2UncoveredFile(contig, readId, read):
    uncoveredFile = OUTPUT_DIR + "/" + contig + "/uncovered.fas"
    if not os.path.exists(uncoveredFile):
        with safe_open_w(uncoveredFile) as f:
            #f = open(uncoveredFile,"w+")
            f.write(">"+contig +"\n")
            f.write(getRefSeq(contig)+"\n")
            #f.close()
        # end with
    # end if

    f = open(uncoveredFile,"a+")
    f.write(">" + readId +"\n")
    f.write(read+"\n")
    f.close()
# end def

def dumpReads2UnmappedFile(contig, readId, read):
    unmappedFile = OUTPUT_DIR + "/" + "unmapped.fas"
    if not os.path.exists(unmappedFile):
        with safe_open_w(unmappedFile) as f:
            f.write("NOT MAPPED TO ANY CONTIG\n")
        # end with
    # end if

    f = open(unmappedFile,"a+")
    f.write(">" + readId + "_" + contig + "\n")
    f.write(read+"\n")
    f.close()
# end def

def dumpContigSSRReads(locusName, refSeq, typeLength, mappedReads):
    locusTypeFile = OUTPUT_DIR + "/" +  locusName + "/SSR" + typeLength + ".fas"
    if not os.path.exists(locusTypeFile):
        with safe_open_w(locusTypeFile) as f:
            f.write(">" + locusName + "\n" + refSeq + "\n")
        # end with
    # end if

    f = open(locusTypeFile,"a+")
    f.write(mappedReads)
    f.close()


def dumpContigTypingStat(locusName, allMotifs, repeatInfo, readsCount, validReads, totalReads, proportion):
    #print OUT "#Site	Motif	Repeat_len	Reads_num	Valid_reads	Total_reads	Proportion\n";
    '''
    #Site	Motif	Repeat_len	Reads_num	Valid_reads Total_reads	Proportion
    P28	CTG	12	4	1273	1273	0.00314218381775334
    P28	CTG	15	28	1273	1273	0.0219952867242734

    P07	AT_AAAC	10_16	1	1659	1659	0.000602772754671489
    P07	AT_AAAC	12_16	2	1659	1659	0.00120554550934298
    '''
    locusTypingStatFile = OUTPUT_DIR + "/" + locusName + "/" + locusName + ".ssr.stat"
    if not os.path.exists(locusTypingStatFile):
        with safe_open_w(locusTypingStatFile) as f:
            f.write("#Site	Motif	Repeat_len	Reads_num	Valid_reads	Total_reads	Proportion\n")
        # end with
    # end if

    f = open(locusTypingStatFile,"a+")
    f.write(locusName + "\t" + allMotifs + "\t" + repeatInfo + "\t" + readsCount + "\t" +
            validReads + "\t" + totalReads + "\t" +  proportion + "\n")
    f.close()
# end def


def refInfoDataFun(refInfoData):
    def getRefInfoFun(locus):
        return refInfoData.get(locus, None)
    # end def
    return getRefInfoFun
# end def

def getRefAllMotifs(locus):
    motifsInfo = getRefInfo(locus)
    allMotifs = ''
    for motifInfo in motifsInfo:
        allMotifs = allMotifs + motifInfo['motif'] + "_"
    # end for
    return allMotifs[:-1]
# end def

# test
# print (getRefInfo('P07'))
# print (getRefSeq('P28'))
# print (ref_stat_data)
# print(getRefAllMotifs('P07'))

def refSequenceDataFun(refSequenceData):
    def getRefSeqFun(locus):
        return refSequenceData.get(locus, None)
    # end def
    return getRefSeqFun
# end def

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i",
                    help="the input bam")
    parser.add_argument("-p",
                    help="the pos information of ref file")
    parser.add_argument("-r",
                    help="the ref file")
    parser.add_argument("-o",
                    help="the output folder")
    args = parser.parse_args()
    OUTPUT_DIR = args.o
    ref_stat_data, ref_sequence_data = prepareRef.getRefData(args.r, args.p)
    getRefSeq = refSequenceDataFun(ref_sequence_data)
    getRefInfo = refSequenceDataFun(ref_stat_data)

    mappedReads = {} # a dictionary with site as key, e.g: mappedReads = {"P01":1200, "P28": 1500}
    validReads = {} # a dictionary with site as key, format same as previous, but ommit reads count of covered
    ssrReadIds = {} # record the read id of each variants

    for line in csv.reader(sys.stdin, dialect="excel-tab"): #You can also use delimiter="\t" rather than giving a dialect.
        # process sam file line by line
        contig  = line[2]
        readId = line[0]
        read = line[9]
        contigInfo = getRefInfo(contig)
        if not contigInfo: # bypass this read if no reference found; move to unmapped reads file
            dumpReads2UnmappedFile(contig, readId, read)
            continue
        # end if

        # put all reads to a hashtable
        if not mappedReads.get(contig, None):
            mappedReads[contig] = dict() # same as {}
        # end if
        mappedReads[contig][readId] = read

        matchStart = int(line[3]) # 3rd column, RNAME of the site, columns after contig P01, is POS: mapped position of base 1 of a read on the reference sequence
        cigar = line[5]

        allCovered = True
        ssrLength = []

        # Start to process the variants
        for motifInfo in contigInfo: # Handle the more than 1 motif scenario
            isSsrCoverd = isSsrRegionCovered.is_ssr_region_covered(matchStart, motifInfo["ssr_pos_left"],
                                                             motifInfo["ssr_pos_right"], cigar )
            if not isSsrCoverd:
                allCovered = False
            # end if

            cigarResult = cigarResolved.cigar_resolved(matchStart, motifInfo["ssr_pos_left"],
                                                             motifInfo["ssr_pos_right"], cigar, motifInfo["motif_length"])
            repeat = round(cigarResult[1] / motifInfo["motif_length"])

            length =  (repeat + motifInfo["repeat_times"]) * motifInfo["motif_length"]
            length = int(length)
            ssrLength.append(length)
        # end for

        if not allCovered: # if not cover all the SSR region, moves to uncovered.fas
            dumpReads2UncoveredFile(contig, line[0], line[9])
            continue
        # end if

        # record the covered reads
        if not validReads.get(contig, None):
            validReads[contig] = dict() # same as {}
        # end if
        validReads[contig][readId] = read

        ssrLengthStr = "_".join(str(x) for x in ssrLength)
        if not ssrReadIds.get(contig, None):
            ssrReadIds[contig] = dict()
        # end if
        ssrReadIds[contig][readId] = ssrLengthStr

    # end for

    for locusName in ref_stat_data: # such as P06, P28
        ssrLengthCount = {}
        ssrLengthReads = {}

        if not mappedReads.get (locusName, None):
            continue
        # end if

        for readId in ssrReadIds[locusName]:
            ssrLength = ssrReadIds[locusName][readId]
            ssrLengthCount[ssrLength] = ssrLengthCount.get(ssrLength, 0) + 1
            ssrLengthReads[ssrLength] = ssrLengthReads.get(ssrLength, '') + ">" +  \
                readId + "\n" + mappedReads[locusName][readId] + "\n"

        # end for

        refSeq = getRefSeq(locusName)
        for ssrTypeLength in ssrLengthCount:
            dumpContigSSRReads(locusName, refSeq, ssrTypeLength, ssrLengthReads[ssrTypeLength])
            repeatInfo = ssrTypeLength
            readsCount = ssrLengthCount[ssrTypeLength]
            validReadsCount = len(validReads[locusName])
            totalReadsCount = len(mappedReads[locusName])
            allMotifs = getRefAllMotifs(locusName)
            proportion = readsCount *1.0 / validReadsCount
            dumpContigTypingStat(locusName, allMotifs, repeatInfo, str(readsCount),
                                 str(validReadsCount), str(totalReadsCount), str(proportion))

            # end for
        # end for
    # end for
    print ('Process broad analysis done.' )
# end if

import pandas as pd
import argparse


def getMotifDict(refStatFile):
    motifDict = {}
    refStatDf = pd.read_csv(refStatFile, sep='\t', lineterminator='\n')
    for index, row in refStatDf.iterrows():
        if row['SSR.No'] ==1:
            motifDict[row['#ID']] = row['Motif']
        # end if
    # end for
    return motifDict
# end def

# test
# refStatFile="ref/sites.motif.info.stats"
# motifDict = getMotifDict(refStatFile)
# print(motifDict)

def safe_open_w(path):
    ''' Open "path" for writing, creating any parent directories as needed.
    '''
    mkdir_p(os.path.dirname(path))
    return open(path, 'w')
# end def

def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc: # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else: raise
    # end try
# end def


def findSsrInfo(sequence, motif):
    maxRepeat = int(len(sequence)/len(motif))
    repeatTimes =  maxRepeat
    while repeatTimes > 0:
        if motif * repeatTimes in sequence:
            return repeatTimes
        # end if
        repeatTimes -= 1
    # end while
    return 0
# end def

# test
# sequence = 'TCTCTAATGATGATGCGGATG'
# motif = 'TGA'
# print(findSsrInfo(sequence, motif))
# print('Done.')


def getReadsSeq(readsFile):
    readsFileReader = open(readsFile)

    line = readsFileReader.readline()
    reads = {}

    previousSeq = ''
    readId=''
    while line:
        if line[0:1] == '>':
            if len(previousSeq)>0:
                reads[readId] = previousSeq
            # end if
            readId = line.rstrip('\n').lstrip('>')
            previousSeq='' # reset
        else:
            previousSeq += line.rstrip('\n')
        # end if

        line = readsFileReader.readline()
    # end while
    # Add the last read
    reads[readId] = previousSeq
    readsFileReader.close()

    return reads
# end def


def dumpReadsToFile(repeats, readsSeq, readsSeqDict, outputFolder):
    outputFile = "%s/SSR%d.fas"%(outputFolder, repeats)
    output = open(outputFile, 'w+')
    for readId in readsSeq:
        output.write(">%s\n%s\n"%(readId, readsSeqDict[readId]))
    # end for
    output.close()
# end def


import os

def statReads(fltFas, locus, readsFile, refStatFile, outputFolder):
    readsSeqDict = getReadsSeq(readsFile)
    motifDict = getMotifDict(refStatFile)
    motif = motifDict[locus]
    ssrData = []
    readsFileReader = open(fltFas)

    line = readsFileReader.readline()
    # get info
    while line:
        if line[0:1] == '>':
            sequence = readsFileReader.readline()
            repeats = findSsrInfo(sequence, motif)
            readId = line.rstrip('\n').lstrip('>')
            if readId != locus: 
            	ssrData.append({'readId':readId, 'repeats': repeats, 'sequence':sequence.rstrip('\n')})
            # end if
        # end if
        line = readsFileReader.readline()
    # end while
    readsFileReader.close()

    # stat
    ssrInfo = {} # key: repeats, value: reads num
    ssrReadsInfo = {} # key: repeats, value: reads list
    readsCount =0
    for ssr in ssrData:
        readsCount += 1
        if not ssr['repeats'] in ssrInfo:
            ssrInfo[ssr['repeats']] = 1
            ssrReadsInfo[ssr['repeats']] = [ssr['readId']]
        else:
            ssrInfo[ssr['repeats']] += 1
            ssrReadsInfo[ssr['repeats']].append(ssr['readId'])
        # end if
    # end for

    # output result
    # #Site   Motif   Repeat_len      Reads_num       Total_reads     Proportion
    title = "#Site\tMotif\tRepeat_len\tReads_num\tTotal_reads\tProportion\n"

    locusTypingStatFile = outputFolder + "/" + locus + ".ssr.stat"
    if not os.path.exists(locusTypingStatFile):
        with safe_open_w(locusTypingStatFile) as f:
            f.write(title)
        # end with
    # end if

    f = open(locusTypingStatFile,"a+")
    for repeats in ssrInfo.keys():
        dumpReadsToFile(repeats* len(motif), ssrReadsInfo[repeats], readsSeqDict, outputFolder )
        proportion = ssrInfo[repeats] * 1.0 / readsCount
        f.write(locus + "\t" + motif + "\t" + str(repeats * len(motif)) + "\t" + str(ssrInfo[repeats]) + "\t" +
             str(readsCount) + "\t" +  str(proportion) + "\n")
    f.close()
# end def

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-l",
                    help="the locus name")
    parser.add_argument("-f",
                    help="the bwa sequence file")
    parser.add_argument("-m",
                    help="the POS file of references")
    parser.add_argument("-r",
                    help="the ssr region sequences file")
    parser.add_argument("-o",
                    help="the output folder")
    args = parser.parse_args()
    fltFas = args.r
    locus = args.l
    readsFile = args.f
    refStatFile = args.m
    outputFolder = args.o

    statReads(fltFas, locus, readsFile, refStatFile, outputFolder)
    print ('Process precise analysis done.' )

# test
# OUTPUT_DIR = "output"
# fltFas = "data/s459130.bwa.sort.fasta.blastn.flt.fas"
# AppledeMacBook-Pro:data holibut$ cat s459130.bwa.sort.fasta.blastn.flt.fas | wc -l
#    9816

# readsFile="data/s459130.bwa.sort.fasta"
# locus = 's459130'
# statReads(fltFas, locus, readsFile)
# print('Done. ')

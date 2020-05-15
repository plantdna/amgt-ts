import csv
import argparse

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

def generateSeq(ssrPosFile, readsFile, outputFile):
    readsSeqDict = getReadsSeq(readsFile)

    output = open(outputFile, 'w+')
    with open(ssrPosFile) as tsv:
        for line in csv.reader(tsv, dialect="excel-tab"): #You can also use delimiter="\t" rather than giving a dialect.
            start=int(line[1])
            end = int(line[2])
            output.write(">%s\n%s\n"%(line[0], readsSeqDict[line[0]][start:end-1]))
        # end for
    # end with
    output.close()
# end def

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-s",
                    help="the SSR pos file")
    parser.add_argument("-b",
                    help="the bwa sequence file")
    parser.add_argument("-o",
                    help="the output folder")
    args = parser.parse_args()
    ssrPosFile = args.s
    readsFile = args.b
    outputFile = args.o

    generateSeq(ssrPosFile, readsFile, outputFile)

    # test
    # ssrPosFile="output/s459130.bwa.sort.fasta.blastn.flt.bed"
    # readsFile="data/s459130.bwa.sort.fasta"
    # outputFile="output/s459130.bwa.sort.fasta.blastn.flt.fas"

import sys
import csv
import argparse

def processBlastFile(leftBlastFile, rightBlastFile, outputBedFile):
    readLength={}
    rightMatchHead={}
    flankRight={}
    leftMatchTail={}
    flankLeft={}
    output = open(outputBedFile, "w+")

    with open(rightBlastFile) as tsv:
        for line in csv.reader(tsv, dialect="excel-tab"): #You can also use delimiter="\t" rather than giving a dialect.
            if line[0][0:1]=='#': continue
            readId=line[2]
            rightMatchHead[readId] = int(line[11]) + 5
            readLength[readId] = int(line[3])
            flankRight[readId] = int(line[9]) - int(line[6]) - int(line[7]) - int(line[8])
        # end for
    # end with

    with open(leftBlastFile) as tsv:
        for line in csv.reader(tsv, dialect="excel-tab"): #You can also use delimiter="\t" rather than giving a dialect.
            if line[0][0:1]=='#': continue
            readId=line[2]
            leftMatchTail[readId] = int(line[12]) - 5
            readLength[readId] = int(line[3])
            flankLeft[readId] = int(line[9]) - int(line[6]) - int(line[7]) - int(line[8])
        # end for
    # end with

    for readId in rightMatchHead.keys():
        if readId in leftMatchTail:
            if leftMatchTail[readId] < rightMatchHead[readId]:
                output.write("%s\t%d\t%d\n"%(readId,leftMatchTail[readId] , rightMatchHead[readId]))
            else:
                if flankRight[readId] > flankLeft[readId]:
                    output.write("%s\t%d\t%d\n"%(readId,0 , rightMatchHead[readId]))
                else:
                    output.write("%s\t%d\t%d\n"%(readId,leftMatchTail[readId] , readLength[readId]))
                # end if
            # end if
        else:
            output.write("%s\t%d\t%d\n"%(readId, 0 , rightMatchHead[readId]))
        # end if
    # end for

    for readId in leftMatchTail.keys():
        if readId not in rightMatchHead:
            output.write("%s\t%d\t%d\n"%(readId, leftMatchTail[readId] , readLength[readId]))
        # end if
    # end for
    output.close()
    print("Process blast files done.")
# end def

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-l",
                    help="the left blast name")
    parser.add_argument("-r",
                    help="the right blast file")
    parser.add_argument("-o",
                    help="the output bed file")
    args = parser.parse_args()
    rightBlastFile = args.r
    leftBlastFile = args.l
    outputBedFile = args.o

    processBlastFile(leftBlastFile, rightBlastFile, outputBedFile)

    # test
    # blastnLeftFile="data/s459130.bwa.sort.fasta.lf.blastn.flt"
    # blastnRightFile="data/s459130.bwa.sort.fasta.rf.blastn.flt"

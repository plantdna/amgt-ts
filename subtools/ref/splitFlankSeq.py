import sys, os, os.path
import errno
import pandas as pd

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


def outputFlank(site, direction, flank):
    appendixDict = {'left':'lf.fas', 'right':'rf.fas'}

    lLankFile = "ref/flank/%s/%s.%s"%(direction, site, appendixDict[direction])
    if not os.path.exists(lLankFile): 
        with safe_open_w(lLankFile) as f:
            f.write(">" + site + "\n" + flank + "\n")
        # end with
    # end if
# end def

def getSiteFlank(site, sequence, flankLength, refStatDf):
    print('site, sequence, flankLength, refStatDf', site, sequence, flankLength, refStatDf)
    ssrStart = int(refStatDf.loc[refStatDf['#ID'] == site, 'Start'])
    ssrEnd = int(refStatDf.loc[refStatDf['#ID'] == site, 'End'])
    lFlank = sequence[ssrStart- flankLength -1:ssrStart-1]
    rFlank = sequence[ssrEnd:ssrEnd+ flankLength]
    return lFlank, rFlank
# end def



def splitFlankSeq(flankLength, refFile, refStatFile):
    refStatDf = pd.read_csv(refStatFile, sep='\t', lineterminator='\n')
    refSequenceReader = open(refFile)
    line = refSequenceReader.readline()
    lineIndex = 0
    while line:
        lineIndex = lineIndex+ 1
        if lineIndex % 2 == 1:
            contigTmp = line
        else:
            site = contigTmp.rstrip('\n').lstrip('>')
            sequence = line.rstrip('\n')
            lFlank, rFlank = getSiteFlank(site, sequence, flankLength, refStatDf)
            outputFlank(site, 'left', lFlank)
            outputFlank(site, 'right', rFlank)
        # end if

        line = refSequenceReader.readline()
    # end while

    refSequenceReader.close()
# end def

if __name__ == "__main__":
    flankLength = int(sys.argv[1])
    refFile = sys.argv[2]
    refStatFile = sys.argv[3]

    splitFlankSeq(flankLength, refFile, refStatFile)
# end if

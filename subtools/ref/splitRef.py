import sys, os, os.path
import errno

# Taken from https://stackoverflow.com/a/600612/119527
def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc: # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else: raise
        # end if
    # end try
# end def

def safe_open_w(path):
    ''' Open "path" for writing, creating any parent directories as needed.
    '''
    mkdir_p(os.path.dirname(path))
    return open(path, 'w')
# end def

def outputSite(folder, site, sequence):
    siteFile = "%s/site/%s.fa"%(folder, site)
    if not os.path.exists(siteFile): 
        with safe_open_w(siteFile) as f:
            f.write(">" + site + "\n" + sequence + "\n")
        # end with
    # end if
# end def

if __name__ == "__main__":
    refFolder = sys.argv[1]
    refFile = sys.argv[2]
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
            outputSite(refFolder, site, sequence)
        # end if

        line = refSequenceReader.readline()
    # end while

    refSequenceReader.close()
# end if

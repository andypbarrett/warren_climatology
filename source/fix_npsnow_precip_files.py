#----------------------------------------------------------------------
# Fixes lines on NPSNOW precip files that contain *****.  I assume that
# these are -9.9 missing or no precipitation values.
#----------------------------------------------------------------------
import shutil
import os

def fix_file(filepath):
    """
    Replaces ***** with -9.9
    """

    shutil.move(filepath, filepath+'.old')
    with open(filepath+'.old', 'r') as infile, open(filepath, 'w') as outfile:
        outfile.write(infile.read().replace('*****',' -9.9'))

    return
            
        
# Returned by grep '\*\*\*' *.pre in ~/data/NPSNOW/precip
lines = """np_08_61.pre:  8  5  1 1961*****  1
           np_08_61.pre:  8  5  5 1961*****  1
           np_08_61.pre:  8  5 10 1961*****  1
           np_08_61.pre:  8  5 12 1961*****  1
           np_08_61.pre:  8  5 15 1961*****  1
           np_08_61.pre:  8  5 27 1961*****  1
           np_16_69.pre: 16  3 24 1969*****  1
           np_18_70.pre: 18  1 16 1970*****  1
           np_30_90.pre: 30  5 30 1990*****  1"""

DIRPATH = '/home/apbarret/data/NPSNOW/precip'

def main():

    # Get list of unique files
    filelist = set([l.split(':')[0] for l in lines.split('\n')])

    # Copy files to *.old
    for f in filelist:
        fix_file(os.path.join(DIRPATH,f.strip()))

if __name__ == "__main__":
    main()
    


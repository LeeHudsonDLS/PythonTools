import sys
import os


lineString = ""
if len(sys.argv) < 2:
    print "Too few arguments\n"
    quit()

if sys.argv[1] == '-h':
    print """Strips the comments from a file. 2nd arg is the character that you want to recognise as a comment (no arg defaults to #). Result is in FILENAME + noComments\n<FILENAME> <COMMENT_CHARACTERS> """
    quit()

if len(sys.argv) > 2:
    commentSyntaxString = sys.argv[2]
else:
    commentSyntaxString = '#'

f = open(sys.argv[1], "r")
for x in f: 
    if commentSyntaxString not in x:
        lineString += x

fileNameConstruction = sys.argv[1].split('.')
destinationFile = fileNameConstruction[0] + 'noComments.' + fileNameConstruction[1]
with open(destinationFile,'w') as f:
        f.write("%s" % lineString)




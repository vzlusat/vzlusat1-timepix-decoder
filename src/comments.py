comments = []
ids = []

def parseComments():

    try:
        infile = open("comments.txt", "r")
    except:
        return 0

    i = 0
    idx = 0

    # for all lines in the file 
    for line in infile:

        # parse the timestamp
        if i == 0:
            ids.append(int(line[0:-1]))

        # parse the first line of tle
        if i == 1:
            comments.append(str(line[0:-1]))

        i += 1

        if i == 2:
            i = 0

def getComment(idx):

    try:
        comment_idx = ids.index(idx)
        comment = comments[comment_idx]
        return comment
    except:
        print("Did not find comment for idx: {}".format(idx))
        return ""

def isAdrenalin(idx):

    comment = getComment(idx)

    if comment.find("#adrenalin") > -1:
        return True
    else:
        return False

def isAnomaly(idx):

    comment = getComment(idx)

    if comment.find("#anomaly") > -1:
        return True
    else:
        return False

def isXrb(idx):

    comment = getComment(idx)

    if comment.find("#xrb") > -1:
        return True
    else:
        return False

def isForLearning(idx):

    comment = getComment(idx)

    if comment.find("#nolearn") > -1:
        return False
    else:
        return True

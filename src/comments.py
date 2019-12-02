global comments
comments = []
ids = []

def parseComments():

    global comments
    comments = []

    try:
        infile = open("comments.txt", "r")
    except:
        return 0

    i = 0
    idx = 0

    # for all lines in the file 
    for line in infile:

        # parse the idx
        if i == 0:
            ids.append(int(line[0:-1]))

        # parse the text
        if i == 1:
            comments.append(str(line[0:-1]))

        i += 1

        if i == 2:
            i = 0

def getComment(idx):

    global comments

    try:
        comment_idx = ids.index(idx)
        comment = comments[comment_idx]
        return comment
    except:
        print("Did not find comment for idx: {}".format(idx))
        return ""

def addTag(idx_in, tag):

    global comments

    print("adding tag: idx_in: {}, tag: {}".format(idx_in, tag))

    lines = []

    with open ('comments.txt', 'r') as infile:
        lines = infile.readlines()

    i = 0
    i = 0

    with open('comments.txt', 'w') as outfile:

        for idx,line in enumerate(lines):

            if i == 0:
                image_idx = int(line[0:-1])
                outfile.write(line)

            if i == 1:
                text = str(line[0:-1])

                if image_idx == idx_in: # we found the line

                    new_line = text + " " + tag + "\n"

                    outfile.write(new_line)
                    print("found idx {}, new_line: {}".format(idx_in, new_line))

                else:
                    outfile.write(line)

            i += 1

            if i == 2:
                i = 0

    parseComments()

def removeTag(idx_in, tag):

    global comments

    print("removing tag: idx_in: {}, tag: {}".format(idx_in, tag))

    lines = []

    with open ('comments.txt', 'r') as infile:
        lines = infile.readlines()

    i = 0
    i = 0

    with open('comments.txt', 'w') as outfile:

        for idx,line in enumerate(lines):

            if i == 0:
                image_idx = int(line[0:-1])
                outfile.write(line)

            if i == 1:
                text = str(line[0:-1])

                if image_idx == idx_in: # we found the line

                    new_line = line
                    new_line = new_line.replace(" "+tag, "")
                    new_line = new_line.replace(tag, "")
                    new_line = new_line.replace("  ", " ")

                    outfile.write(new_line)

                else:
                    outfile.write(line)

            i += 1

            if i == 2:
                i = 0

    parseComments()

def isAdrenalin(idx):

    global comments

    comment = getComment(idx)

    if comment.find("#adrenalin") > -1:
        return True
    else:
        return False

def isAnomaly(idx):

    global comments

    comment = getComment(idx)

    if comment.find("#anomaly") > -1:
        return True
    else:
        return False

def isXrb(idx):

    global comments

    comment = getComment(idx)

    if comment.find("#xrb") > -1:
        return True
    else:
        return False

def isNolearn(idx):

    global comments

    comment = getComment(idx)

    if comment.find("#nolearn") > -1:
        return True
    else:
        return False

def isForLearning(idx):

    global comments

    comment = getComment(idx)

    if comment.find("#nolearn") > -1:
        return False
    else:
        return True

def hasExposure(idx):

    global comments

    comment = getComment(idx)

    if comment.find("#exposure") > -1:
        return True
    else:
        return False 

def getExposure(idx):

    global comments

    comment = getComment(idx)

    if comment.find("#exposure") > -1:
        strip_start=comment[comment.find("#exposure")+9:]
        time=strip_start[:strip_start.find("#")]
        return int(time)
    else:
        return 0

def hasMode(idx):

    global comments

    comment = getComment(idx)

    if (comment.find("#tot") > -1) or (comment.find("#mpx") > -1):
        return True
    else:
        return False

def getMode(idx):

    global comments

    comment = getComment(idx)

    if comment.find("#tot") > -1:
        return 1
    else:
        return 0

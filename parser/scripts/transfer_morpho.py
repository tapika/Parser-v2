import sys

ID,FORM,LEMMA,UPOS,XPOS,FEAT,HEAD,DEPREL,DEPS,MISC=range(10)

def read_conllu(f):
    sent=[]
    comment=[]
    for line in f:
        line=line.strip()
        if not line: # new sentence
            if sent:
                yield comment,sent
            comment=[]
            sent=[]
        elif line.startswith("#"):
            comment.append(line)
        else: #normal line
            sent.append(line.split("\t"))
    else:
        if sent:
            yield comment, sent



def transfer_token(token):
    new_xpos="XPOS={x}|{feat}".format(x=token[XPOS],feat=token[FEAT])
    token[XPOS]=new_xpos
    return token

def detransfer_token(token):
    if token[XPOS]=="_": # must be reinserted multiwordtoken
        token[FEAT]="_" # make sure it does not leak information
        return token
    if "|" not in token[XPOS]:
        print("something weird:",token, file=sys.stderr)
        token[FEAT]="_"
        return token
    xpos,feat=token[XPOS].split("|",1)
    token[XPOS]=xpos.split("=",1)[1]
    token[FEAT]=feat
    return token

def process_batch(data, detransfer=True):

    lines=[]
    for comm,sent in read_conllu(data.split("\n")):
        for c in comm:
            lines.append(c)
        for token in sent:
            if detransfer==True:
                token=detransfer_token(token)
            else:
                token=transfer_token(token)
            lines.append("\t".join(token))
        lines.append("")
    return("\n".join(lines))

def main(args):
    for comm, sent in read_conllu(sys.stdin):
        for c in comm:
            print(c)
        for token in sent:
            if args.detransfer:
                token=detransfer_token(token)
            else:
                token=transfer_token(token)
            print("\t".join(token))
        print()


if __name__=="__main__":

    import argparse

    parser = argparse.ArgumentParser(description='')
    g=parser.add_argument_group("Reguired arguments")
    
    g.add_argument('--detransfer', action="store_true", default=False, help='Detransfer, return xpos and features to the correct fields.')
    
    args = parser.parse_args()

    main(args)


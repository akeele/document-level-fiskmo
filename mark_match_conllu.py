import sys
import gzip

conllu_file = sys.argv[1]
parallel_sentences_file = sys.argv[2]
#new_conllu_file = sys.argv[3]
language_number = sys.argv[3]

parallel_sentences = []
with open(parallel_sentences_file, "rt") as f:
    for line in f:
        line = line.strip()
        fields = line.split("\t")
        parallel_sentences.append(fields[int(language_number)])


#new_conllu = open(new_conllu_file, "wt")
with gzip.open(conllu_file, "rt") as conllu:
    for line in conllu:
        line = line.strip()
        if line.startswith("# text"):
            sentence = line.lstrip("# text = ")
            for i, parallel_sentence in enumerate(parallel_sentences):
                if sentence == parallel_sentence:
                    print("# parallel hit line = {}".format(i))
                    break
        print(line)

#new_conllu.close()

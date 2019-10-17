import sys
import argparse
import gzip
from collections import OrderedDict
from itertools import groupby


def read_articles(conllu_file):
    articles = []
    with gzip.open(conllu_file, "rt") as conllu:
        parallel_hit_line = None 
        article_sentences = []
        for line in conllu:
            line = line.strip()
            # new sentence
            if not line:
                parallel_hit_line = None
            
            if line.startswith("# parallel"):
                parallel_hit_line = int(line.lstrip("# parallel hit line = "))

            if line.startswith("# text"):
                article_sentence = line[9:]
                if not article_sentence:
                    continue
                if parallel_hit_line:
                    article_sentence = [parallel_hit_line, article_sentence]
                article_sentences.append(article_sentence)

            if line.startswith("# newdoc"):
                if article_sentences:
                    articles.append(article_sentences)
                    article_sentences = []
    return articles

def get_parallel_hit_articles(articles):
    parallel_hit_articles = {}
    for idx, article in enumerate(articles):
        for sentence in article:
            if isinstance(sentence, list):
                parallel_hit_articles[idx] = article
                break
    return parallel_hit_articles

def move_parallel_hits_to_top(parallel_hit_articles):
    new_parallel_hit_articles = {}
    for ID, article in parallel_hit_articles.items():
        new_article = []
        parallel_hits = []
        for sentence in article:
            if isinstance(sentence, list):
                parallel_hits.append(sentence[0])
                new_article.append(sentence[1])
            else:
                new_article.append(sentence)
        new_parallel_hit_articles[ID] = [parallel_hits, new_article]
    return new_parallel_hit_articles

def find_matching_articles(source_articles, target_articles):
    source_parallel_hit_articles = get_parallel_hit_articles(source_articles)
    target_parallel_hit_articles = get_parallel_hit_articles(target_articles)
    
    source_parallel_hit_articles = move_parallel_hits_to_top(source_parallel_hit_articles)
    target_parallel_hit_articles = move_parallel_hits_to_top(target_parallel_hit_articles)
    """
    parallel_hits = []
    parallel_articles = []
    parallel_ids = []
    for source_ID, source_article in source_parallel_hit_articles.items():
        source_hits = source_article[0]
        if not source_article[1]:
            continue
        for target_ID, target_article in target_parallel_hit_articles.items():
            target_hits = target_article[0]
            if not target_article[1]:
                continue
            # ADD ALL ARTICLES THAT MATCH
            if not set(source_hits).isdisjoint(target_hits):
                parallel_hits.append(list(set(source_hits) & set(target_hits)))
                parallel_articles.append([source_article[1], target_article[1]])
                parallel_ids.append((source_ID, target_ID))
                break
    return parallel_hits, parallel_articles, parallel_ids
    """
    return source_parallel_hit_articles, target_parallel_hit_articles

def write_parallel_hits_to_file(parallel_hits, output_file):
    with open(output_file, "wt") as output:
        for hit in parallel_hits:
            print(hit, file=output)

def write_parallel_articles_to_file(parallel_articles, output_file):
    output = open(output_file, "wt")
    for article in parallel_articles:
        for source_sentence in article[0]:
            print(source_sentence, file=output)
        print("|||", file=output)
        for target_sentence in article[1]:
            print(target_sentence, file=output)
        print("@@@", file=output)
    output.close()

def write_parallel_ids_to_file(parallel_ids, output_file):
    output = open(output_file, "wt")
    for ids in parallel_ids:
        print(ids[0], ids[1], sep="|", file=output)
    output.close()

def write_articles_to_file(output_file, articles):
    with open(output_file, "wt") as output:
        for _, article in articles.items():
            hit_lines = [str(item) for item in article[0]]
            print(",".join(hit_lines), file=output)
            for sentence in article[1]:
                print(sentence, file=output)
            print("|||", file=output)

if __name__ == "__main__":
    
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument("--source_conllu", help="Source conllu file")
    argument_parser.add_argument("--target_conllu", help="Target conllu file")
    argument_parser.add_argument("--source_articles_out", help="Output file for source articles")
    argument_parser.add_argument("--target_articles_out", help="Output file for target articles")
    """
    argument_parser.add_argument("--parallel_hits_out", help="Output file for parallel hits")
    argument_parser.add_argument("--parallel_articles_out", help="Output file for parallel articles")
    argument_parser.add_argument("--parallel_ids_out", help="Output file for parallel IDs")
    """
    arguments = argument_parser.parse_args()

    source_articles = read_articles(arguments.source_conllu)
    target_articles = read_articles(arguments.target_conllu)
    
    source_parallel_hit_articles, target_parallel_hit_articles = find_matching_articles(source_articles, target_articles)
    write_articles_to_file(arguments.source_articles_out, source_parallel_hit_articles)
    write_articles_to_file(arguments.target_articles_out, target_parallel_hit_articles)
    """
    parallel_hits, parallel_articles, parallel_ids = find_matching_articles(source_articles, target_articles)
    
    write_parallel_hits_to_file(parallel_hits, arguments.parallel_hits_out)
    
    write_parallel_articles_to_file(parallel_articles, arguments.parallel_articles_out)

    write_parallel_ids_to_file(parallel_ids, arguments.parallel_ids_out)
    """

import numpy
import sys
import gzip
import operator
from sklearn.preprocessing import normalize
import argparse
import time


DIMENSIONS = 1024

def read_embeddings(embeddings_file, number_of_embeddings):
    embeddings = numpy.memmap(embeddings_file, dtype='float32', mode='r', shape=(number_of_embeddings, DIMENSIONS))
    return embeddings
"""
def read_embeddings(embeddings_file, n):
    embeddings = numpy.fromfile(embeddings_file, dtype=numpy.float32)
    embeddings.resize(embeddings.shape[0] // DIMENSIONS, DIMENSIONS)
    return embeddings
"""
def read_original_sentences(original_sentence_file):
    with open(original_sentence_file, "rt") as f:
        original_sentences = f.readlines()
    original_sentences = [sentence.strip() for sentence in original_sentences]
    return original_sentences

# TODO 
def read_parallel_articles(parallel_articles_file):
    with open(parallel_articles_file, "rt") as f:
        parallel_articles = f.read()
        parallel_articles = parallel_articles.split("\n|||\n")

        parallel_hits = [article.split("\n")[0] for article in parallel_articles]
        parallel_articles = [article.split("\n")[1:] for article in parallel_articles]
        parallel_articles = ["\n".join(article) for article in parallel_articles]
    return parallel_hits[:-1], parallel_articles[:-1] # Last one is empty


def get_sentence_dict(original_sentences, embeddings):
    assert len(original_sentences) == embeddings.shape[0]
    sentence_dict = {sentence: idx for (idx, sentence) in enumerate(original_sentences)}
    return sentence_dict

def create_parallel_dict(parallel_articles, parallel_hits, keys):
    assert len(parallel_articles) == len(parallel_hits)
    parallel_dict = {}
    for article, hits in zip(parallel_articles, parallel_hits):
        hits = hits.split(",")
        hits = [int(hit) for hit in hits]
        
        if keys == "hits":
            for hit in hits:
                parallel_dict.setdefault(hit, []).append(article)
        elif keys == "articles":
            parallel_dict[article] = hits
        else:
            print("Wrong keys argument. Choose from [hits, articles]")

    return parallel_dict

def get_max_cosines_in_articles(source_parallel_articles, \
                                target_parallel_articles, \
                                source_sentence_dict, \
                                target_sentence_dict, \
                                source_embeddings, \
                                target_embeddings, \
                                source_parallel_dict, \
                                target_parallel_dict):

    all_parallel_articles_and_margin_scores = []
    source_errors = 0
    target_errors = 0
    for source_article, hits in source_parallel_dict.items():
        source_article_sentences = source_article.strip().split("\n")
        source_indices = []
        for sentence in source_article_sentences:
            try:
                source_indices.append(source_sentence_dict[sentence])
            except KeyError:
                source_errors += 1
                continue

        target_hit_articles = []
        for hit in hits:
            hit_articles = target_parallel_dict[hit]
            target_hit_articles += hit_articles
        target_hit_articles = list(set(target_hit_articles))
        
        target_hit_articles_max_cosines = []
        for target_hit_article in target_hit_articles:
            target_hit_article_sentences = target_hit_article.strip().split("\n")
            target_indices = []
            for sentence in target_hit_article_sentences:
                try:
                    target_indices.append(target_sentence_dict[sentence])
                except KeyError:
                    target_errors += 1
                    continue
        
            source_matrix = source_embeddings[source_indices]
            target_matrix = target_embeddings[target_indices]
        
            cosine_matrix = numpy.dot(normalize(source_matrix, axis=1), normalize(target_matrix, axis=1).T)
            max_sentence_cosines = numpy.amax(cosine_matrix, axis=1)
            target_hit_articles_max_cosines.append(target_hit_article, numpy.mean(max_sentence_cosines))

        target_hit_articles_max_cosines.sort(key=lambda tup: tup[1], reverse=True)
        margin_score = target_hit_articles_max_cosines[0][1] / numpy.mean(target_hit_articles_max_cosines[1:][1])
        
        parallel_articles_and_margin_score = (source_article, target_hit_articles_max_cosines[0][0], margin_score)
        all_parallel_articles_and_margin_scores.append(parallel_articles_and_margin_score)

    print("Source key errors: ", source_errors)
    print("Target key errors: ", target_errors)
    return all_parallel_articles_and_margin_scores

def sort_parallel_articles(parallel_articles_and_scores):
    sorted_parallel_articles = sorted(parallel_articles_and_scores, key=lambda tup: tup[2], reverse=True)
    return sorted_parallel_articles

def write_to_output_file(sorted_parallel_articles, output_file):
    with open(output_file, "wt") as output:
        for parallel_article in sorted_parallel_articles:
            print(parallel_article[0], file=output)
            print("@@@", file=output)
            print(parallel_article[1], file=output)
            print("|||")


if __name__ == "__main__":
   
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument("--source-embeddings", help="File of source language sentence embeddings")
    argument_parser.add_argument("--target-embeddings", help="File of target language sentence embeddings")
    argument_parser.add_argument("--source-sentences", help="Original source language sentences file")
    argument_parser.add_argument("--target-sentences", help="Original target language sentences file")
    argument_parser.add_argument("--parallel-source-articles", help="File with parallel source articles")
    argument_parser.add_argument("--parallel-target-articles", help="File with parallel target articles")
    argument_parser.add_argument("--output", help="Output file")
    arguments = argument_parser.parse_args()

    source_embeddings_file = arguments.source_embeddings
    target_embeddings_file = arguments.target_embeddings
    source_original_file = arguments.source_sentences
    target_original_file = arguments.target_sentences
    parallel_source_articles_file = arguments.parallel_source_articles
    parallel_target_articles_file = arguments.parallel_target_articles
    output = arguments.output
    
    source_original_sentences = read_original_sentences(source_original_file)
    target_original_sentences = read_original_sentences(target_original_file)
    print("Original sentences read.")

    source_embeddings = read_embeddings(source_embeddings_file, len(source_original_sentences))
    target_embeddings = read_embeddings(target_embeddings_file, len(target_original_sentences))
    print("Embeddings read.")

    source_sentence_dict = get_sentence_dict(source_original_sentences, source_embeddings)
    target_sentence_dict = get_sentence_dict(target_original_sentences, target_embeddings)
    print("Sentence dictionaries created.")
    
    parallel_source_hits, parallel_source_articles = read_parallel_articles(parallel_source_articles_file)
    parallel_target_hits, parallel_target_articles = read_parallel_articles(parallel_target_articles_file)
    
    source_parallel_dict = create_parallel_dict(parallel_source_articles, parallel_source_hits, keys="hits")
    target_parallel_dict = create_parallel_dict(parallel_target_articles, parallel_target_hits, keys="articles")

    print("Parallel articles read.")
    print("{} parallel articles.".format(len(parallel_source_articles))) 
    print("Calculating cosine similarities...")
    start = time.time()
    # TODO
    parallel_articles_and_margin_scores = get_max_cosines_in_articles(source_parallel_articles, \
                                                                      target_parallel_articles, \
                                                                      source_sentence_dict, \
                                                                      target_sentence_dict, \
                                                                      source_embeddings, \
                                                                      target_embeddings, \
                                                                      source_parallel_dict, \
                                                                      target_parallel_dict):

    end = time.time()
    print("Cosine calculations took {:.4f} seconds".format(end - start))
    print("Sorting articles...")
    sorted_parallel_articles = sort_parallel_articles(parallel_articles_and_margin_scores)
    
    print("Writing results to file...")
    print(sorted_parallel_articles[:10][2])
    write_to_output_file(sorted_parallel_articles, output)

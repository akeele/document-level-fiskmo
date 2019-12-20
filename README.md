# document-level-fiskmo
Document level parallel matching

## Mark the sentences in conllu file
```
python mark_match_conllu.py CONLLU_FILE PARALLEL_SENTENCES_FILE LANGUAGE_NUMBER > NEW_CONLLU_FILE
```
The `LANGUAGE_NUMBER` is either 1 or 2 depending on the language of the conllu file. 1 is the first language in the `PARALLEL_SENTENCE_FILE` and 2 is the second. Run this for the both languages. 

## Find matching documents
```
python find_matching_documents.py --source_conllu SOURCE_CONLLU \
                                  --target_conllu TARGET_CONLLU \
                                  --source_articles_out SOURCE_ARTICLES_OUT \
                                  --target_articles_out TARGET_ARTICLES_OUT
```
This finds the documents from marked conllus from the previous step. Spits out the documents (articles) for both languages. The output files have the following structure:
```
4857,9484
Minulla on koira.
|||
309
Tässä on kahvia.
.
.
.
```
The numbers are the parallel hits found in the previous step. Then is the document and the document separator `|||`

## Score documents
```
python document_max_cosine.py --source-embeddings SOURCE_EMBEDDINGS \
                              --target-embeddings TARGET_EMBEDDINGS \
                              --source-sentences SOURCE_SENTENCES \
                              --target-sentences TARGET_SENTENCES \
                              --parallel-source-articles PARALLEL_SOURCE_ARTICLES \
                              --parallel-target-articles PARALLEL_TARGET_ARTICLES \
                              --output OUTPUT_FILE                               
```
The embeddings are from the original sentences and the sentence files are the original sentences which were then embedded. The parallel articles are from the previous step. Mean of max cosine along the shorter axis of the dot product between the documents is taken. Outputs the parallel documents sorted by the margin score, which is the best mean cosine divided by the other parallel document candidates.

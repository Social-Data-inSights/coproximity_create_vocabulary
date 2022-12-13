# wordpiece_ngrams

Method to try to extract ngrams from the text itself using the [wordpiece algorithm](https://arxiv.org/abs/1609.08144v2). Does not work well because it is difficult to differentiate genuine key expressions and colloquial expression.


## Scripts

### compare_old_new.ipynb

Compare 2 ngrams results

### create_ngram_wordpiece.py

Main method to try to extract ngrams from the text itself using the wordpiece algorithm

### test_create_ngram.py

Basic test for the ngrams creator
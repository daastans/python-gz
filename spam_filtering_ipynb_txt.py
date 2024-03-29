# -*- coding: utf-8 -*-
"""Spam Filtering.ipynb.txt

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1thgBfPu7FUzCa2PQD48wDbKZBBrkMZ0x
"""

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import string

from google.colab import files
uploaded = files.upload()

"""# Read Data"""

#read dataset
spam_df = pd.read_csv('spam.csv', encoding="ISO-8859-1")

#subset and rename columns
spam_df = spam_df[['v1', 'v2']]
spam_df.rename(columns={'v1': 'spam', 'v2': 'text'}, inplace=True)

#convert spam column to binary
spam_df.spam = spam_df.spam.apply(lambda s: True if s=='spam' else False)

#lowercase everything and remove punctuation
spam_df.text = spam_df.text.apply(lambda t: t.lower().translate(str.maketrans('', '', string.punctuation)))

#shuffle
spam_df = spam_df.sample(frac=1)

spam_df

for t in spam_df[spam_df.spam == True].iloc[:5].text:
    print(t)
    print('-------')

for t in spam_df[spam_df.spam == False].iloc[:5].text:
    print(t)
    print('-------')

#get training set
train_spam_df = spam_df.iloc[:int(len(spam_df)*0.7)]

#get testing set
test_spam_df = spam_df.iloc[int(len(spam_df)*0.7):]

FRAC_SPAM_TEXTS = train_spam_df.spam.mean()
print(FRAC_SPAM_TEXTS)

"""# Create Spam Bag of Words and Non-Spam Bag of Words"""

#get all words from spam and non-spam datasets
train_spam_words = ' '.join(train_spam_df[train_spam_df.spam == True].text).split(' ')
train_non_spam_words = ' '.join(train_spam_df[train_spam_df.spam == False].text).split(' ')

common_words = set(train_spam_words).intersection(set(train_non_spam_words))

train_spam_bow = dict()
for w in common_words:
    train_spam_bow[w] = train_spam_words.count(w) / len(train_spam_words)

train_non_spam_bow = dict()
for w in common_words:
    train_non_spam_bow[w] = train_non_spam_words.count(w) / len(train_non_spam_words)

"""# Predict on Test Set

# $ P(\text{SPAM} | \text{"urgent please call this number"}) $
# $\propto P(\text{"urgent please call this number"} | \text{SPAM}) \times P(\text{SPAM}) $
# $= P(\text{"urgent"} | \text{SPAM}) \times P(\text{"please"} | \text{SPAM}) \times \dots \times P(\text{SPAM})$

# Due to numerical issues, equivalently  compute:

# $log(P(\text{"urgent"} | \text{SPAM}) \times P(\text{"please"} | \text{SPAM}) \times \dots \times P(\text{SPAM}))$
# $ = log(P(\text{"urgent"} | \text{SPAM})) + log(P(\text{"please"} | \text{SPAM})) + \dots + log(P(\text{SPAM}))$
"""

def predict_text(t, verbose=False):
    #if some word doesnt appear in either spam or non-spam BOW, disregard it
    valid_words = [w for w in t if w in train_spam_bow]
    
    #get the probabilities of each valid word showing up in spam and non-spam BOW
    spam_probs = [train_spam_bow[w] for w in valid_words]
    non_spam_probs = [train_non_spam_bow[w] for w in valid_words]
    
    #print probs if requested
    if verbose:
        data_df = pd.DataFrame()
        data_df['word'] = valid_words
        data_df['spam_prob'] = spam_probs
        data_df['non_spam_prob'] = non_spam_probs
        data_df['ratio'] = [s/n if n > 0 else np.inf for s,n in zip(spam_probs, non_spam_probs)]
        print(data_df)
     
    #calculate spam score as sum of logs for all probabilities
    spam_score = sum([np.log(p) for p in spam_probs]) + np.log(FRAC_SPAM_TEXTS)
    
    #calculate non-spam score as sum of logs for all probabilities
    non_spam_score = sum([np.log(p) for p in non_spam_probs]) + np.log(1-FRAC_SPAM_TEXTS)
    
    #if verbose, report the two scores
    if verbose:
        print('Spam Score: %s'%spam_score)
        print('Non-Spam Score: %s'%non_spam_score)
   
    #if spam score is higher, mark this as spam
    return (spam_score >= non_spam_score)

predict_text('urgent call this number'.split(), verbose=True)

predict_text('hey do you want to go a movie tonight'.split(), verbose=True)

predict_text(''.split(), verbose=True)

predict_text('Huryy the offer ends today'.split(), verbose=True)

predictions = test_spam_df.text.apply(lambda t: predict_text(t.split()))

frac_spam_messages_correctly_detected = np.sum((predictions == True) & (test_spam_df.spam == True)) / np.sum(test_spam_df.spam == True)
print('Fraction Spam Correctly Detected: %s'%frac_spam_messages_correctly_detected)

frac_valid_sent_to_spam = np.sum((predictions == True) & (test_spam_df.spam == False)) / np.sum(test_spam_df.spam == False)
print('Fraction Valid Messages Sent to Spam: %s'%frac_valid_sent_to_spam)


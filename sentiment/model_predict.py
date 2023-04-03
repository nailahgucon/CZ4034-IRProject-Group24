import re
import string
import os
import pickle
import nltk
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
nltk.download('punkt')
nltk.download('wordnet')

import pandas as pd
from sklearn.preprocessing import LabelBinarizer
import keras
from keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from keras.models import Sequential
from keras.layers import Dense, Embedding, GRU, LSTM, Bidirectional
from tensorflow.keras.layers import Embedding
from keras.initializers import Constant
from keras.callbacks import ModelCheckpoint
from keras.models import load_model


socialmedia_abbv = pd.read_csv(f'{os.getcwd()}/sentiment/additional_data/socialmedia_abbreviations.csv')

def clean_text(text):
    
    # remove links and tags -- irrelevant to sentiment
    pattern = re.compile('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
    text = pattern.sub('', text)
    text = " ".join(filter(lambda x:x[0]!='@', text.split()))

    text = text.lower()

    # normalise social media abbreviations
    text_list = text.split(" ")
    for ind, row in socialmedia_abbv.iterrows():
      text_list = [row.Text if i==row.Abbreviations else i for i in text_list]
    text = " ".join(text_list)

    # sub short forms
    text = re.sub(r"i'm", "i am", text)
    text = re.sub(r"he's", "he is", text)
    text = re.sub(r"she's", "she is", text)
    text = re.sub(r"that's", "that is", text)        
    text = re.sub(r"what's", "what is", text)
    text = re.sub(r"where's", "where is", text) 
    text = re.sub(r"\'ll", " will", text)  
    text = re.sub(r"\'ve", " have", text)  
    text = re.sub(r"\'re", " are", text)
    text = re.sub(r"\'d", " would", text)
    text = re.sub(r"\'ve", " have", text)
    text = re.sub(r"won't", "will not", text)
    text = re.sub(r"don't", "do not", text)
    text = re.sub(r"did't", "did not", text)
    text = re.sub(r"can't", "can not", text)
    text = re.sub(r"it's", "it is", text)
    text = re.sub(r"couldn't", "could not", text)
    text = re.sub(r"have't", "have not", text)
    text = re.sub(r"[,.\"\'!@#$%^&*(){}?/;`~:<>+=-]", "", text)
    
    # remove punctuations, numbers
    text = ' '.join(filter(lambda x:x.isalpha(), text.split(' ')))

    #tokenize
    tokens = word_tokenize(text)

    # remove stop words
    # stop_words = set(stopwords.words("english")) # chose not to use NLTK stopwords since it removes words like "not", affect sentiment analysis
    stop_words = set(['i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', "you're", "you've", "you'll", "you'd", 'your', 'yours', 'yourself', 'yourselves', 
                    'he', 'him', 'his', 'himself', 'she', "she's", 'her', 'hers', 'herself', 'it', "it's", 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves', 
                    'what', 'which', 'who', 'whom', 'this', 'that', "that'll", 'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 
                    'having', 'do', 'does', 'did', 'doing', 'a', 'an', 'the', 'and', 'if', 'or', 'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with', 'about', 
                    'between', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again', 
                    'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'nor', 
                    'only', 'own', 'same', 'so', 'than', 's', 'will', 'just', 'should', "should've", 'now', 'd', 'll', 'm', 'o', 're', 've', 'y', 'ma'])
    tokens = [w for w in tokens if not w in stop_words]

    # lemmatization
    lemmatizer = WordNetLemmatizer()
    filtered_tokens = [lemmatizer.lemmatize(t) for t in tokens]

    return filtered_tokens

def model_predict(filepath):
    df = pd.read_csv(filepath)

    # preprocess df
    df['Review_processed'] = df['Review'].apply(clean_text)

    # load models
    modelpath = f'{os.getcwd()}/sentiment/models/'
    subjectivity_model = keras.models.load_model(f"{modelpath}subject_model.h5")
    polarity_model = keras.models.load_model(f"{modelpath}sentiment_bilstm")
    # spam_model = keras.models.load_model.load(f"{modelpath}spam_lstm.h5")

    # predict subjectivity
    token_data = pd.read_csv(f'{os.getcwd()}/additional_data/token_data.csv')
    tokenizer = Tokenizer(num_words=50000, oov_token='<OOV>')
    tokenizer.fit_on_texts(token_data)

    lb = LabelBinarizer()
    lb.fit([1,1,1,1,0,1,1,0,1,1,1])
    df['Sentiment'] = df['Review_processed'].apply(predict_subjectivity, args=(tokenizer, subjectivity_model, lb))

    # predict polarity
    with open(f'{os.getcwd()}/sentiment/additional_data/seq_list', 'rb') as fp:
      seq_list = pickle.load(fp)
    tokenizer_obj = Tokenizer()
    tokenizer_obj.fit_on_texts(seq_list)
    df_opiniated = df[df['Sentiment'] == 'opiniated']
    df_opiniated['Polarity'] = df_opiniated['Review_processed'].apply(predict_polarity, args=(tokenizer_obj, polarity_model))

    # merge ['neutral', 'opiniated'] with ['positive', 'negative']
    df_merged = df.merge(df_opiniated, on=['Name', 'Category', 'Style', 'Star', 'Date', 'Rating', 'ReviewTitle', 'Review'], how='left')
    df_merged['Sentiment'] = df_merged.apply(lambda row: row['Sentiment_x'] if row['Sentiment_x']=='neutral' else row['Polarity'], axis=1)
    df_merged = df_merged.drop(columns=['Polarity', 'Sentiment_x', 'Sentiment_y', 'Review_processed_x', 'Review_processed_y'])
    df_merged = df_merged.loc[:, ~df_merged.columns.str.contains('^Unnamed')]

    # save file
    filename = filepath.split('/')[-1][:-4]
    df_merged.to_csv(f'{os.getcwd()}/{filename}_predicted.csv')

# each models predictions
def predict_subjectivity(s, tokenizer, subjectivity_model, labelbinarizer):
    seq = tokenizer.texts_to_sequences([' '.join(s)])
    padded = pad_sequences(seq)
    pred = subjectivity_model.predict(padded, verbose=0)

    # Get the label name back
    result = labelbinarizer.inverse_transform(pred)[0]
    if result==0: return "neutral" 
    else: return "opiniated"
   
def predict_polarity(s, tokenizer_obj, polarity_model, max_length = 25):
    test_sequences = tokenizer_obj.texts_to_sequences([s])
    test_review_pad = pad_sequences(test_sequences, maxlen=max_length, padding='post')
    pred = polarity_model.predict(test_review_pad, verbose=0)
    pred*=100
    if pred[0][0]>=50: return "positive" 
    else: return "negative"
   

model_predict(f'{os.getcwd()}/reviews_combined.csv')
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from collections import Counter
import re


def clean_tokenized_text(doc):
    '''
    INPUT: STRING
    OUTPUT: LIST OF STRINGS
    Cleans the text from punctuation, non-alpha content, stopwords and
    web related words and returns the cleaned tokenized text
    '''
    rx = re.compile('\W+')
    # CLEAN PUNCTUATION AND NON ALPHA CONTENT
    text = rx.sub(" ", doc).strip().lower()
    excllist = [u'html', u'jpg', u'gif', u'index', u'onion', u'http',
                u'image', u'login', u'img', u'thumb', u'site', u'post',
                u'png', u'com', u'net', u'not', u'les', u'page',
                u'domains', u'url', u'txt', u'link', u'tor', u'the',
                u'font', u'pdf', u'onions', u'logout', u'file', u'web',
                u'pic', u'email', u'mail', u'www', u'result', u'imgs',
                u'images', u'sql', u'home', u'jpeg', u'icons']
    stoplist = stopwords.words('english') + excllist
    # RUN LEMMATIZER
    wnl = WordNetLemmatizer()
    split_cleaned_text = []
    for word in text.split():
        temp = wnl.lemmatize(word, pos='v')
        if len(temp) > 2 and temp.isalpha() and temp not in stoplist:
            split_cleaned_text.append(temp)
    return split_cleaned_text

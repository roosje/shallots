from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

def clean_tokenized_text(doc, rx):
        #cleaning punctuation and non alpha content
        text = rx.sub(" ", doc).strip()
        stoplist = stopwords.words('english')
        #lemmatizing
        wnl= WordNetLemmatizer()
        split_cleaned_text = [wnl.lemmatize(word.lower(), pos='v') for word in text.split() if \
                       (word.isalpha() and word not in stoplist and len(word)>1)]
        return split_cleaned_text
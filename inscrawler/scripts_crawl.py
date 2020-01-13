
# importing the requests library 
import requests 
import time
import json
import pandas as pd

from place import Place
from google.cloud import language
from google.cloud.language import enums
from google.cloud.language import types
from google.cloud import translate
# api-endpoint 
URL_POST = "https://api.apify.com/v2/actor-tasks/5Qr9ky9pCjPoWMBop/run-sync?token=ykNEY72FBgMGpTu49Pfq5RpaL&ui=1"
URL_GET = "https://api.apify.com/v2/actor-tasks/5Qr9ky9pCjPoWMBop/runs/last/dataset/items?token=ykNEY72FBgMGpTu49Pfq5RpaL"
import os
os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="/home/pain/Downloads/bitcat-40862d8e3192.json"

def analyze_sentiment(text):
    client = language.LanguageServiceClient()

    # text_content = 'I am so happy and joyful.'

    # Available types: PLAIN_TEXT, HTML
    type_ = enums.Document.Type.PLAIN_TEXT

    # Optional. If not specified, the language is automatically detected.
    # For list of supported languages:
    # https://cloud.google.com/natural-language/docs/languages
    lang = "en"
    document = {"content": text, "type": type_, "language": lang}

    # Available values: NONE, UTF8, UTF16, UTF32
    encoding_type = enums.EncodingType.UTF8

    response = client.analyze_sentiment(document, encoding_type=encoding_type)

    # for sentence in response.sentences:
        
    return response

def sample_translate_text(text, target_language, project_id):
    """
    Translating Text

    Args:
      text The content to translate in string format
      target_language Required. The BCP-47 language code to use for translation.
    """

    client = translate.TranslationServiceClient()

    # TODO(developer): Uncomment and set the following variables
    # text = 'Text you wish to translate'
    # target_language = 'fr'
    # project_id = '[Google Cloud Project ID]'
    contents = [text]
    parent = client.location_path(project_id, "global")

    response = client.translate_text(
        parent=parent,
        contents=contents,
        mime_type='text/plain',  # mime types: text/plain, text/html
        source_language_code='vi',
        target_language_code=target_language)
    # Display the translation for each input text provided
    for translation in response.translations:
        print(u"Translated text: {}".format(translation.translated_text))

    return response

if __name__== "__main__":
    key_word = "Ẩm Thực Tân Bùi "
    payload ={
    "searchString": key_word,
    "proxyConfig": {
        "useApifyProxy": True
    },
    "includeReviews": True,
    "includeImages": False,
    "includeHistogram": False,
    "includeOpeningHours": False,
    "includePeopleAlsoSearch": False,
    "zoom": 10,
    "maxCrawledPlaces": 1,
    "debug": False
    }

    headers = {'Content-type': 'application/json'}

    # rs_post = requests.post(url=URL_POST, data=json.dumps(payload), headers=headers)
    rs_get = requests.get(url=URL_GET)

    # extracting data in json format 
    response = rs_get.json()[0]

    place = Place()
    place.name = response.get('title')
    place.reviewer_quant = response.get('reviewsCount')
    place.stars = response.get('totalScore')
    reviews = response.get('reviews')
    reviews = pd.DataFrame(reviews).drop_duplicates().to_dict('records')
    place.comments = len(reviews)
    for rv in reviews:
        
        place.update_star(rv.get('stars'))
        comment = rv.get('text')
        if comment == None:
            continue
        elif comment.startswith('(Translated by Google)'):
            comment = comment.split('(Translated by Google)')[-1][1:]
            comment = comment.split('\n\n(Original)\n')[0]
        else:
            tsl = sample_translate_text(comment, "en-US", "bitcat")
            comment = tsl.translations[0].translated_text

        analyze_cmt = analyze_sentiment(comment)
        print(rv.get('name'))
        print(analyze_cmt.document_sentiment.score)
        place.update_comments(analyze_cmt.document_sentiment.score)

    # printing the output 
    print() 

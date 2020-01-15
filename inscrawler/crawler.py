from __future__ import unicode_literals

import glob
import json
import os
import re
import sys
import time
import traceback

from builtins import open
from time import sleep

from datetime import datetime
from tqdm import tqdm

from . import secret
from .place import Place 
from .browser import Browser
from .exceptions import RetryException
from .fetch import fetch_caption
from .fetch import fetch_comments
from .fetch import fetch_datetime
from .fetch import fetch_imgs
from .fetch import fetch_likers
from .fetch import fetch_likes_plays
from .fetch import fetch_details
from .utils import instagram_int
from .utils import randmized_sleep
from .utils import retry

from google.cloud import translate
from google.cloud import language
from google.cloud.language import enums
from google.cloud.language import types
from langdetect import detect
from langdetect import DetectorFactory
DetectorFactory.seed = 0


class Logging(object):
    PREFIX = "instagram-crawler"

    def __init__(self):
        try:
            timestamp = int(time.time())
            self.cleanup(timestamp)
            self.logger = open("/tmp/%s-%s.log" % (Logging.PREFIX, timestamp), "w")
            self.log_disable = False
        except Exception:
            self.log_disable = True

    def cleanup(self, timestamp):
        days = 86400 * 7
        days_ago_log = "/tmp/%s-%s.log" % (Logging.PREFIX, timestamp - days)
        for log in glob.glob("/tmp/instagram-crawler-*.log"):
            if log < days_ago_log:
                os.remove(log)

    def log(self, msg):
        if self.log_disable:
            return

        self.logger.write(msg + "\n")
        self.logger.flush()

    def __del__(self):
        if self.log_disable:
            return
        self.logger.close()


class InsCrawler(Logging):
    # URL = "https://www.instagram.com"
    RETRY_LIMIT = 10

    def __init__(self, has_screen=False):
        super(InsCrawler, self).__init__()
        self.browser = Browser(has_screen)
        self.page_height = 0

    def get_user_profile(self):
        browser = self.browser
        # url = "%s/%s/" % (InsCrawler.URL, username)
        url = "https://www.google.com/maps/place/Qu%C3%A1n+%C4%82n+Bi%E1%BB%83n+Xanh/@10.8096823,106.7092435,14z/data=!4m8!1m2!2m1!1sbien+xanh!3m4!1s0x317527a6c94abdf3:0x28eb4efba2da6210!8m2!3d10.844343!4d106.7660651"
        browser.get(url)
        name = browser.find_one(".GLOBAL__gm2-headline-5")
        print(name.text)
        star = browser.find_one(".section-star-display")
        # if not star:
        #     return {
        #     "name": name.text,
        #     "star": None,
        #     "review_no": None
        # }
        reviews_no = browser.find_one(".widget-pane-link")
        print(reviews_no.text)
        return {
            "name": name.text,
            "star": star.text,
            "review_no": reviews_no.text
        }

    def get_user_posts(self):
        user_profile = self.get_user_profile()
        # if not number:
        #     number = instagram_int(user_profile["post_num"])
        place = Place()
        place.name = user_profile["name"]

        # self._dismiss_login_prompt()

        # if detail:
        self._get_posts_full(place)
        rs = {
                "name" : place.name,
                "comments" : place.comments,
                "comments_s" : place.comments_s,
                "comments_a" : place.comments_a,
                "comments_b" : place.comments_b,
                "comments_c" : place.comments_c,
                "comments_d" : place.comments_d,
                "comments_e" : place.comments_e,
                "comments_f" : place.comments_f,
                "comments_g" : place.comments_g,
                "comments_h" : place.comments_h,
                "comments_i" : place.comments_i,
                "stars" : place.stars,
                "star1s" : place.star1s,
                "star2s" : place.star2s,
                "star3s" : place.star3s,
                "star4s" : place.star4s,
                "star5s" : place.star5s
        }
        return rs

    def _get_posts_full(self, place):
        browser = self.browser
        # place = Place()
        show_more_button = browser.find_one(".allxGeDnJMl__taparea")
        if show_more_button:
            show_more = browser.find_one("button", show_more_button)
            if show_more:
                show_more.location_once_scrolled_into_view
                show_more.click()
                time.sleep(0.5)

        ########### Section for place not have show more button #############
        else:
            ele_comments = browser.find(".section-review")
            self._parse_comment(ele_comments, place)
            return
        ########### End section for place not have show more button #############


        ########### Section for place have show more button #############
        jquery_js = open('/home/pain/Desktop/DCLV/jquery-3.4.1.min.js', 'r')
        jquery = jquery_js.read() #read the jquery from a file
        browser.driver.execute_script(jquery) #active the jquery lib
        try:
            for i in range(2000):
                print(i)
                browser.driver.execute_script("$('.section-loading.noprint' )[0].scrollIntoView()")
                time.sleep(0.2)
                # browser.implicitly_wait(1)
        except:
            pass
        
        comment_section = browser.find(".section-layout")
        if len(comment_section) == 6:
            ele_comments = browser.find(".section-review-content", comment_section[5])
            self._parse_comment(ele_comments, place)
        
        return
        ########### End section for place have show more button #############

    def _parse_comment(self, ele_comments, place):
        browser = self.browser
        reviews = []
        tsl_document = ""
        for ele in ele_comments:
            author = browser.find_one(".section-review-title", ele)
            comment = browser.find_one(".section-review-review-content", ele)
            star_eles = browser.find(".section-review-star-active", ele)
            star_num = len(star_eles)
            place.update_star(star_num)
            text = comment.text
            if text != '':
                if text.startswith('(Translated by Google)'):
                    text = text.split('(Translated by Google)')[-1][1:]
                    text = text.split('\n\n(Original)\n')[0]
                else:
                    if detect(text) in ('vi', 'pt', 'tl', 'fi'):
                        tsl = sample_translate_text(text, "en-US", "bitcat")
                        text = tsl.translations[0].translated_text
                if text[-1] == ".":
                    tsl_document += text + " i @ i. " 
                else:
                    tsl_document += text + ". i @ i. " 
                # anal_text = analyze_sentiment(text)
                # place.update_comments(anal_text.document_sentiment.score)
                cmt = comment.text

            else:
                cmt = None
            review_ele = {
                "author": author.text,
                "comment": cmt,
                "star_num": star_num
            }
            reviews.append(review_ele)

        anal_doc = analyze_sentiment(tsl_document)
        sentence_sentiment = 0
        sentence_num = 0
        for index, sentence in enumerate(anal_doc.sentences):
            print(index)
            if "i @ i" in sentence.text.content and sentence_num != 0:
                place.update_comments(sentence_sentiment / sentence_num)
                print(sentence_sentiment)
                sentence_sentiment = 0
                sentence_num = 0
                continue
            sentence_sentiment += sentence.sentiment.score
            sentence_num += 1
        return reviews

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

    



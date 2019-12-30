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
    URL = "https://www.instagram.com"
    RETRY_LIMIT = 10

    def __init__(self, has_screen=False):
        super(InsCrawler, self).__init__()
        self.browser = Browser(has_screen)
        self.page_height = 0

    def _dismiss_login_prompt(self):
        ele_login = self.browser.find_one(".Ls00D .Szr5J")
        if ele_login:
            ele_login.click()

    def login(self):
        browser = self.browser
        url = "%s/accounts/login/" % (InsCrawler.URL)
        browser.get(url)
        u_input = browser.find_one('input[name="username"]')
        u_input.send_keys(secret.username)
        p_input = browser.find_one('input[name="password"]')
        p_input.send_keys(secret.password)

        login_btn = browser.find_one(".L3NKy")
        login_btn.click()

        @retry()
        def check_login():
            if browser.find_one('input[name="username"]'):
                raise RetryException()

        check_login()

    def get_user_profile(self):
        browser = self.browser
        # url = "%s/%s/" % (InsCrawler.URL, username)
        url = "https://www.google.com/maps/place/Ph%C6%A1%CC%89+bo%CC%80+Thi%C3%AAn+%C4%90i%C3%AA%CC%80n/@9.9092005,105.3183807,17z/data=!3m1!4b1!4m5!3m4!1s0x31a0bfcf69fb122f:0x3e7875353d70d283!8m2!3d9.9091952!4d105.3205747?hl=vi-VN"
        browser.get(url)
        name = browser.find_one(".GLOBAL__gm2-headline-5")
        print(name.text)
        star = browser.find_one(".section-star-display")
        if not star:
            return {
            "name": name.text,
            "star": None,
            "review_no": None
        }
        reviews_no = browser.find_one(".widget-pane-link")
        print(reviews_no.text)
        # statistics = [ele.text for ele in browser.find(".g47SY")]
        # post_num, follower_num, following_num = statistics
        return {
            "name": name.text,
            "star": star.text,
            "review_no": reviews_no.text
        }

    def get_user_profile_from_script_shared_data(self, username):
        browser = self.browser
        url = "%s/%s/" % (InsCrawler.URL, username)
        browser.get(url)
        source = browser.driver.page_source
        p = re.compile(r"window._sharedData = (?P<json>.*?);</script>", re.DOTALL)
        json_data = re.search(p, source).group("json")
        data = json.loads(json_data)

        user_data = data["entry_data"]["ProfilePage"][0]["graphql"]["user"]

        return {
            "name": user_data["full_name"],
            "desc": user_data["biography"],
            "photo_url": user_data["profile_pic_url_hd"],
            "post_num": user_data["edge_owner_to_timeline_media"]["count"],
            "follower_num": user_data["edge_followed_by"]["count"],
            "following_num": user_data["edge_follow"]["count"],
            "website": user_data["external_url"],
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
        # else:
        #     return self._get_posts(number)

    def get_latest_posts_by_tag(self, tag, num):
        url = "%s/explore/tags/%s/" % (InsCrawler.URL, tag)
        self.browser.get(url)
        return self._get_posts(num)

    def auto_like(self, tag="", maximum=1000):
        self.login()
        browser = self.browser
        if tag:
            url = "%s/explore/tags/%s/" % (InsCrawler.URL, tag)
        else:
            url = "%s/explore/" % (InsCrawler.URL)
        self.browser.get(url)

        ele_post = browser.find_one(".v1Nh3 a")
        ele_post.click()

        for _ in range(maximum):
            heart = browser.find_one(".dCJp8 .glyphsSpriteHeart__outline__24__grey_9")
            if heart:
                heart.click()
                randmized_sleep(2)

            left_arrow = browser.find_one(".HBoOv")
            if left_arrow:
                left_arrow.click()
                randmized_sleep(2)
            else:
                break

    def _get_posts_full(self, place):
        @retry()
        def check_next_post(cur_key):
            ele_a_datetime = browser.find_one(".eo2As .c-Yi7")
            # It takes time to load the post for some users with slow network
            if ele_a_datetime is None:
                raise RetryException()

            next_key = ele_a_datetime.get_attribute("href")
            if cur_key == next_key:
                raise RetryException()

        browser = self.browser
        # place = Place()
        show_more_button = browser.find_one(".allxGeDnJMl__taparea")
        if show_more_button:
            show_more = browser.find_one("button", show_more_button)
            if show_more:
                show_more.location_once_scrolled_into_view
                show_more.click()
                time.sleep(0.5)
        else:
            ele_comments = browser.find(".section-review")
            reviews = []
            for ele in ele_comments:
                author = browser.find_one(".section-review-title", ele)
                comment = browser.find_one(".section-review-review-content", ele)
                star_eles = browser.find(".section-review-star-active", ele)
                star_num = len(star_eles)
                place.update_star(star_num)
                if comment.text != '':
                    tsl = sample_translate_text(comment.text, "en-US", "bitcat")
                    print(tsl)
                    text = tsl.translations[0].translated_text
                    anal_text = analyze_sentiment(text)
                    place.update_comments(anal_text.document_sentiment.score)
                    cmt = comment.text
                else:
                    cmt = None
                review_ele = {
                    "author": author.text,
                    "comment": cmt,
                    "magnitude": anal_text.document_sentiment.magnitude,
                    "score": anal_text.document_sentiment.score
                }
                reviews.append(review_ele)
            return


        jquery_js = open('/home/pain/Desktop/DCLV/jquery-3.4.1.min.js', 'r')
        jquery = jquery_js.read() #read the jquery from a file
        browser.driver.execute_script(jquery) #active the jquery lib
        try:
            for i in range(20):
                browser.driver.execute_script("$('.section-loading.noprint' )[0].scrollIntoView()")
                time.sleep(0.2)
                # browser.implicitly_wait(1)
        except:
            pass


        
        comment_section = browser.find(".section-layout")
        if len(comment_section) == 5:
            ele_comments = browser.find(".section-review-content", comment_section[4])
            reviews = []
            for ele in ele_comments:
                author = browser.find_one(".section-review-title", ele)
                comment = browser.find_one(".section-review-review-content", ele)
                star_eles = browser.find(".section-review-star-active", ele)
                star_num = len(star_eles)
                place.update_star(star_num)
                if comment.text != '':
                    tsl = sample_translate_text(comment.text, "en-US", "bitcat")
                    print(tsl)
                    text = tsl.translations[0].translated_text
                    anal_text = analyze_sentiment(text)
                    place.update_comments(anal_text.document_sentiment.score)
                    cmt = comment.text
                else:
                    cmt = None
                review_ele = {
                    "author": author.text,
                    "comment": cmt,
                    "magnitude": anal_text.document_sentiment.magnitude,
                    "score": anal_text.document_sentiment.score,
                    "star_num": star_num
                }
                reviews.append(review_ele)
            
        # ele_post = browser.find_one(".v1Nh3 a")
        # ele_post.click()
        # dict_posts = {}

        # pbar = tqdm(total=num)
        # pbar.set_description("fetching")
        # cur_key = None

        # # Fetching all posts
        # for _ in range(num):
        #     dict_post = {}

        #     # Fetching post detail
        #     try:
        #         check_next_post(cur_key)

        #         # Fetching datetime and url as key
        #         ele_a_datetime = browser.find_one(".eo2As .c-Yi7")
        #         cur_key = ele_a_datetime.get_attribute("href")
        #         dict_post["key"] = cur_key
        #         fetch_datetime(browser, dict_post)
        #         #fetch_imgs(browser, dict_post)
        #         fetch_likes_plays(browser, dict_post)
        #         fetch_likers(browser, dict_post)
        #         fetch_caption(browser, dict_post)
        #         fetch_comments(browser, dict_post)

        #         # check if datetime was over a month ago 
        #         a = datetime.strptime(dict_post["datetime"], '%Y-%m-%dT%H:%M:%S.%fZ')
        #         a = time.mktime(a.timetuple())
        #         if time.mktime(datetime.now().timetuple()) - a > 2592000:
        #             break

        #     except RetryException:
        #         sys.stderr.write(
        #             "\x1b[1;31m"
        #             + "Failed to fetch the post: "
        #             + cur_key or 'URL not fetched'
        #             + "\x1b[0m"
        #             + "\n"
        #         )
        #         break

        #     except Exception:
        #         sys.stderr.write(
        #             "\x1b[1;31m"
        #             + "Failed to fetch the post: "
        #             + cur_key if isinstance(cur_key,str) else 'URL not fetched'
        #             + "\x1b[0m"
        #             + "\n"
        #         )
        #         traceback.print_exc()

        #     self.log(json.dumps(dict_post, ensure_ascii=False))
        #     dict_posts[browser.current_url] = dict_post

        #     pbar.update(1)
        #     left_arrow = browser.find_one(".HBoOv")
        #     if left_arrow:
        #         left_arrow.click()

        # pbar.close()
        # posts = list(dict_posts.values())
        # if posts:
        #     posts.sort(key=lambda post: post["datetime"], reverse=True)
        # return posts

    def _get_posts(self, num):
        """
            To get posts, we have to click on the load more
            button and make the browser call post api.
        """
        TIMEOUT = 600
        browser = self.browser
        key_set = set()
        posts = []
        pre_post_num = 0
        wait_time = 1

        pbar = tqdm(total=num)

        def start_fetching(pre_post_num, wait_time):
            ele_posts = browser.find(".v1Nh3 a")
            for ele in ele_posts:
                key = ele.get_attribute("href")
                if key not in key_set:
                    dict_post = { "key": key }
                    ele_img = browser.find_one(".KL4Bh img", ele)
                    dict_post["caption"] = ele_img.get_attribute("alt")
                    dict_post["img_url"] = ele_img.get_attribute("src")

                    fetch_details(browser, dict_post)

                    key_set.add(key)
                    posts.append(dict_post)

                    if len(posts) == num:
                        break

            if pre_post_num == len(posts):
                pbar.set_description("Wait for %s sec" % (wait_time))
                sleep(wait_time)
                pbar.set_description("fetching")

                wait_time *= 2
                browser.scroll_up(300)
            else:
                wait_time = 1

            pre_post_num = len(posts)
            browser.scroll_down()

            return pre_post_num, wait_time

        pbar.set_description("fetching")
        while len(posts) < num and wait_time < TIMEOUT:
            post_num, wait_time = start_fetching(pre_post_num, wait_time)
            pbar.update(post_num - pre_post_num)
            pre_post_num = post_num

            loading = browser.find_one(".W1Bne")
            if not loading and wait_time > TIMEOUT / 2:
                break

        pbar.close()
        print("Done. Fetched %s posts." % (min(len(posts), num)))
        return posts[:num]


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

# def mean(arr):
    



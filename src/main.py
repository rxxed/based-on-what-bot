#!/usr/bin/env python3

import os
import threading
import logging
from urllib.parse import quote_plus
from typing import Callable

import praw
from praw.models import Submission, Subreddit, Comment
from dotenv import load_dotenv

log_format = "%(asctime)s: %(threadName)s: %(message)s"
logging.basicConfig(format=log_format, level=logging.DEBUG, datefmt="%H:%M:%S", filename="log.log")
logger = logging.getLogger(__name__)

# API token info gets loaded from a .env file
load_dotenv()
CLIENT      = os.getenv("CLIENT_ID")
SECRET      = os.getenv("CLIENT_SECRET")
USER_AGENT  = os.getenv("USER_AGENT")
USERNAME    = os.getenv("USERNAME")
PASSWORD    = os.getenv("PASSWORD")

RESPONSE = "Based? Based on what?"
PREPOSITIONS = ["on", "off", "in"]

reddit = praw.Reddit(
        user_agent="based_on_what_bot",
        client_id=CLIENT,
        client_secret=SECRET,
        username=USERNAME,
        password=PASSWORD
)


def restart(handler: Callable):
        """
        Decorator that restarts threads if they fail
        """
        def wrapped_handler(*args, **kwargs):
                logger.info("Starting thread with: %s", args)
                while True:
                        try:
                                handler(*args, **kwargs)
                        except Exception as e:
                                logger.error("Exception: %s", e)
        return wrapped_handler


@restart
def iterate_comments(sub_name):
        sub = reddit.subreddit(sub_name)
        for comment in sub.stream.comments():
                logger.debug(f"Iterating comment {comment.body}: ")
                if is_comment_based(comment):
                        send_reply_to(comment)
                        logger.info(f"Replied to comment {str(comment.body)}")
                else:
                        print(f"Comment ignored: {str(comment.body)}")


@restart
def iterate_posts(sub_name):
        sub = reddit.subreddit(sub_name)
        for post in sub.stream.submissions():
                logger.debug(f"Iterating post {post.title}")
                if is_post_based(post):
                        send_reply_to(post)
                        logger.info(f"Replied to post {str(post.title)}")
                else:
                        logger.debug("Post ignored: {str(comment.body)}")


def send_reply_to(obj):
        obj.reply(RESPONSE)


def is_comment_based(comment: Comment) -> bool:
        body = str(comment.body).lower().split()
        for i, w in enumerate(body):
                if w == "based" and i+1 < len(body):
                        if body[i+1] not in PREPOSITIONS:
                                return True
        return False


def is_post_based(post: Submission) -> bool:
        body = str(post.selftext).lower()
        title = str(post.title).lower()
        for i, w in enumerate(title):
                if w == "based" and i+1 < len(body):
                        if body[i+1] not in PREPOSITIONS:
                                return True
        for i, w in enumerate(body):
                if w == "based" and i+1 < len(body):
                        if body[i+1] not in PREPOSITIONS:
                                return True
        return False


def main():
        logger.info("Main       : Creating threads")
        threads = []
        posts_thread = threading.Thread(
                target=iterate_posts, args=("4chan",), name="posts"
        )
        comments_thread = threading.Thread(
                target=iterate_comments, args=("4chan",), name="comments"
        )

        threads.append(posts_thread)
        threads.append(comments_thread)

        logger.info("Main       : Starting threads")
        for thread in threads:
                thread.start()

if __name__ == '__main__':
        main()

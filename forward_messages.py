from praw.models import Message

import config
import helpers

FORWARD_SUBJECT = "{subject!r} from {author}"
FORWARD_MESSAGE = "New message from /u/{author} re {subject!r}:\n\n---\n\n{body}"


def forward(to):
    reddit = helpers.initialize_reddit()
    to = reddit.redditor(to)

    for item in reddit.inbox.unread(limit=None):

        if not config.testing:
            item.mark_read()

        if isinstance(item, Message):
            author = item.author
            body = item.body
            subject = item.subject

            forward_subject = FORWARD_SUBJECT.format(subject=subject, author=author)
            forward_message = FORWARD_MESSAGE.format(
                author=author, subject=subject, body=body
            )

            if not config.testing:
                try:
                    to.message(subject=forward_subject, message=forward_message)
                except Exception:
                    # just in case, for now.
                    # todo remove this
                    to.message(
                        subject="New message",
                        message="I have a new message, but something went wrong.",
                    )
            else:
                print(
                    "Messaging {} with subject {!r} and message:\n{}".format(
                        to, forward_subject, forward_message
                    )
                )

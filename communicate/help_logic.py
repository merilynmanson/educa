from django.core.exceptions import ObjectDoesNotExist


def get_comment_tree(comment, user):
    likes = comment.commentvote_set.filter(is_like=True).count()
    dislikes = comment.commentvote_set.filter(is_like=False).count()
    try:
        my_vote = comment.commentvote_set.get(user=user).is_like
    except ObjectDoesNotExist:
        my_vote = None

    if comment.replies.all().count() == 0:
        return {
            'content': {
                'text': comment.text,
                'likes': likes,
                'dislikes': dislikes,
                'my_vote': my_vote
            },
            'replies': None
        }

    comment_dict = dict()

    comment_dict['content'] = {
        'text': comment.text,
        'likes': likes,
        'dislikes': dislikes,
        'my_vote': my_vote
    }
    comment_dict['replies'] = {}

    for c in comment.replies.all():
        comment_dict['replies'][f'comment_{c.id}'] = get_comment_tree(c, user)

    return comment_dict

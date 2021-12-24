from django.core.exceptions import ObjectDoesNotExist


def get_comment_tree(comment, user):
    likes = comment.commentvote_set.filter(is_like=True).count()
    dislikes = comment.commentvote_set.filter(is_like=False).count()
    try:
        my_vote = comment.commentvote_set.get(user=user).is_like
    except ObjectDoesNotExist:
        my_vote = None

    comment_dict = dict()

    comment_dict['content'] = {
        'id': comment.id,
        'username': comment.user.username,
        'user_id': comment.user.id,
        'text': comment.text,
        'likes': likes,
        'dislikes': dislikes,
        'date': str(comment.date),
        'my_vote': my_vote
    }
    comment_dict['replies'] = {}

    if comment.replies.all().count() == 0:
        comment_dict['replies'] = None
        return comment_dict

    for c in comment.replies.all():
        comment_dict['replies'][f'comment_{c.id}'] = get_comment_tree(c, user)

    return comment_dict

# -*-coding:UTF-8-*-

from app.comment.handler import CommentNewHandler

urlpattern = (
    (r'/comments/new', CommentNewHandler),
)

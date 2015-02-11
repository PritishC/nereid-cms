# -*- coding: utf-8 -*-
'''

    Nereid User
    user.py

    :copyright: (c) 2010-2014 by Openlabs Technologies & Consulting (P) Ltd.
    :license: GPLv3, see LICENSE for more details

'''
from trytond.pool import Pool, PoolMeta

from nereid import route, request, abort
from werkzeug.contrib.atom import AtomFeed

__all__ = ['NereidUser']
__metaclass__ = PoolMeta


class NereidUser:
    __name__ = 'nereid.user'

    def get_published_articles(self):
        """
        Returns list of articles published by this author
        """
        Article = Pool().get('nereid.cms.article')

        return map(int, Article.search([
            ('author', '=', self.id),
            ('state', '=', 'published'),
        ]))

    def serialize(self, purpose=None):
        """
        Downstream implementation of serialize() which adds serialization for
        atom feeds.
        """
        if purpose == 'atom':
            return {
                'name': self.display_name,
                'email': self.email or None,
            }

    @classmethod
    @route('/article-author/<int:id>.atom')
    def atom_feed(cls, id):
        """
        Returns the atom feed for all articles published under a certain author
        """
        Article = Pool().get('nereid.cms.article')

        try:
            author = cls(id)
        except:
            abort(404)

        feed = AtomFeed(
            "Articles by Author %s" % author.display_name, feed_url=request.url,
            url=request.host_url
        )
        for article_id in author.get_published_articles():
            feed.add(**Article(article_id).serialize(purpose='atom'))

        return feed.get_response()

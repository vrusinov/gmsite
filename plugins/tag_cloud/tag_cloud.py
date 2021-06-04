# -*- coding: utf-8 -*-

# Copyright © 2012-2013 Roberto Alsina and others.

# Permission is hereby granted, free of charge, to any
# person obtaining a copy of this software and associated
# documentation files (the "Software"), to deal in the
# Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the
# Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice
# shall be included in all copies or substantial portions of
# the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY
# KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR
# PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS
# OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR
# OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import json
import os
import dataclasses

import lxml

from nikola.plugin_categories import SignalHandler
from nikola.utils import LocaleBorg

# Max & min size adjustment, in em
MAX_SIZE = 10
MIN_SIZE = 0.65


@dataclasses.dataclass
class Tag:
    name: str
    link: str
    uses: int
    size: float = 0
    size_adj: str = ''


class TagCloud(SignalHandler):

    name = "tag_cloud_shortcode"

    def render_tag_cloud(self, lang):
        posts_per_tag = [
            Tag(name=k, link=f'/{lang}/tags/{k}/', uses=len(v))
            for k, v in self.site.posts_per_classification['tag'][lang].items()
        ]
        max_uses = max(x.uses for x in posts_per_tag)
        min_uses = min(x.uses for x in posts_per_tag)
        range = max_uses - min_uses
        for tag in posts_per_tag:
            size_adj = (
                MIN_SIZE + (tag.uses - min_uses) / range *
                (MAX_SIZE - MIN_SIZE)
            )
            tag.font_size = f'{size_adj:+.2f}em'
        return posts_per_tag

    def set_site(self, site):
        self.site = site
        site._GLOBAL_CONTEXT['tag_cloud'] = self.render_tag_cloud
        return super().set_site(site)

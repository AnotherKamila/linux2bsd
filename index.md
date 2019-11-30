---
title: WIP :D
layout: default
---

hi

{{site.data}}
{{site.data.hw}}
blaaaah?

{% for thingy in site.data.hw %}
  * {{thingy[0]}}: {{thingy[1]}}
{% endfor %}

{% for kv in site.data %}
  {% assign category = kv[0] %}
  {% assign cmds     = kv[1] %}
  * {{category}}: {{cmds}}
{% endfor %}

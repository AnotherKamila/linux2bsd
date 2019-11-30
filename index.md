---
title: WIP :D
layout: default
---

# Linux  ⟷ FreeBSD commands reference

{% for kv in site.data %}
{% assign category = kv[0] %}
{% assign cmds     = kv[1] %}
## {{category}}
{% for cmd in cmds %}
* {{cmd[0]}} → {{cmd[1]}}
{% endfor %}
{% endfor %}

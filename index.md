---
title: WIP :D
layout: default
---

# Linux  ⟷ FreeBSD commands reference

{% for kv in site.data %}
{% assign category = kv[0] %}
{% assign cmds     = kv[1] %}
## {{category}}
<table>
  <thead>
    <tr><td>Linux</td><td>FreeBSD</td></tr>
  </thead>
  <tbody>
{% for cmd in cmds %}
    <tr><td>{{cmd['#linux']}}</td><td>{{cmd.freebsd}}</td></tr>
{% endfor %}
  </tbody>
</table>
{% endfor %}

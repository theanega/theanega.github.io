---
layout: default
title: Digital Garden
---

<div class="garden-list">
  {% for note in site.notes %}
    <div class="garden-entry">
      <h2><a href="{{ note.url }}">{{ note.title }}</a></h2>
      <div class="meta">
        <span class="planted">🌱 Planted: {{ note.planted | date: "%B %d, %Y" }}</span>
        <span class="tended">🌿 Last tended: {{ note.tended | date: "%B %d, %Y" }}</span>
      </div>
      {% if note.excerpt %}
        <p class="excerpt">{{ note.excerpt }}</p>
      {% endif %}
    </div>
  {% endfor %}
</div>
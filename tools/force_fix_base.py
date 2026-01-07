
html_content = """{% load static %}
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{% block title %}Chandran Electronics{% endblock %}</title>
  <link rel="manifest" href="{% static 'manifest.json' %}">
  <link rel="stylesheet" href="{% static 'css/design-system.css' %}">
  <link rel="stylesheet" href="{% static 'css/light-neon.css' %}">
  {% block extra_css %}{% endblock %}
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet">
  <link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">
</head>
<body>
  <!-- Header / Nav -->
  <header class="site-header">
    <div class="container">
      <div class="header-content">
        <div class="logo-container">
          <div class="logo">
            <h1 class="animated-title">⚡ Chandran Electronics</h1>
            <span class="logo-tagline">Future Tech Experience</span>
          </div>
        </div>
        <div class="theme-controls">
          {% if user.is_authenticated %}
            <span class="filter-chip">{{ user.username }}</span>
          {% endif %}
        </div>
      </div>
    </div>
  </header>

  <nav class="navbar ultra-glass">
    <div class="container">
      <div class="nav-content">
        <div class="nav-links">
          <a href="{% url 'ecommerce' %}" class="nav-link">Home</a>
          <a href="{% url 'profile' %}" class="nav-link">Account</a>
          {% if user.is_authenticated %}
            <form method="post" action="{% url 'logout' %}" style="display:inline;">{% csrf_token %}
              <button type="submit" class="logout-btn"><span class="material-icons">logout</span> Logout</button>
            </form>
          {% else %}
            <a href="{% url 'login' %}" class="nav-link">Login</a>
          {% endif %}
        </div>
        <div class="nav-actions">
          <a href="{% url 'cart' %}" class="action-btn cart-btn"><span class="material-icons">shopping_cart</span>{% if cart_count > 0 %}<span class="count-badge">{{ cart_count }}</span>{% endif %}</a>
          <a href="{% url 'wishlist' %}" class="action-btn wishlist-btn"><span class="material-icons">favorite</span>{% if wishlist_count > 0 %}<span class="count-badge">{{ wishlist_count }}</span>{% endif %}</a>
        </div>
      </div>
    </div>
  </nav>

  <!-- Page content -->
  <main>
    {% block content %}{% endblock %}
  </main>

  <!-- Footer -->
  <footer class="site-footer">
    <div class="container">
      <div class="footer-content">
        <div class="footer-brand">
          <h4>⚡ Chandran Electronics</h4>
          <p>Your gateway to the future of technology.</p>
        </div>
        <div class="footer-links">
          <h5>Support</h5>
          <a href="#">Help Center</a>
          <a href="#">Contact</a>
        </div>
      </div>
      <div class="footer-bottom">
        <p>&copy; 2025 Chandran Electronics. All rights reserved.</p>
      </div>
    </div>
  </footer>

  <!-- Shared scripts -->
  <script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.2/gsap.min.js"></script>
  <script src="https://unpkg.com/htmx.org@1.9.10"></script>
  <script src="https://cdn.jsdelivr.net/npm/sweetalert2@11"></script>
  <script src="{% static 'js/lazyload.js' %}"></script>
  <script src="{% static 'js/microinteractions.js' %}"></script>
  <script src="{% static 'js/transitions.js' %}"></script>
  {% block extra_js %}{% endblock %}

  <!-- Service Worker registration -->
  <script>if('serviceWorker' in navigator){window.addEventListener('load',()=>{navigator.serviceWorker.register('{% static "sw.js" %}');});}</script>
</body>
</html>
"""

import os
target_file = r'c:\Users\LENOVO\Desktop\gurutech\encahnceed django-ecommerce\templates\base.html'
with open(target_file, 'w', encoding='utf-8') as f:
    f.write(html_content)
print(f"Successfully overwrote {target_file}")

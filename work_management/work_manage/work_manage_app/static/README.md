# Employee Work Management System

A polished Django landing-page starter for an Employee Work Management System. It uses Django template/static conventions, Bootstrap 5, custom CSS and JavaScript, and original SVG artwork.

## Run with Django

1. Copy `templates/index.html` into a Django app's template directory, or configure `TEMPLATES[0]['DIRS']` to include this project's `templates` folder.
2. Add this project's `static` folder to `STATICFILES_DIRS` in `settings.py`.
3. Render `index.html` from a view:

```python
from django.shortcuts import render

def home(request):
    return render(request, "index.html")
```

4. Add a URL that points to `home`, then run `python manage.py runserver`.

The page uses `{% load static %}` and all local CSS, JavaScript, SVGs, and favicon references are served through Django's static-file system. Bootstrap, Bootstrap Icons, and the Poppins typeface load from their official CDNs.

## Included assets

- Responsive premium landing page with navigation, hero, features, workflow, statistics, testimonials, contact form, and footer.
- Full-screen animated laptop loader, reveal animation, counter animation, floating cards, smooth scrolling, and contact-form validation.
- Original SVG logo and illustrations under `static/images`.

#!/usr/bin/env bash
set -o errexit

python manage.py collectstatic --no-input
python manage.py makemigrations
python manage.py migrate

# Buat akun admin otomatis dan isi data dummy jika database kosong
python manage.py shell -c "
from django.contrib.auth import get_user_model;
User = get_user_model();
User.objects.filter(username='admin').exists() or User.objects.create_superuser('admin', 'admin@example.com', 'admin123');

from courses.models import Course, SiteSetting;
import os; os.system('python add_pro_content.py');

setting, _ = SiteSetting.objects.get_or_create(id=1);
setting.site_name = 'LMS';
setting.save();
"

exec gunicorn config.wsgi:application --bind 0.0.0.0:${PORT:-8080}

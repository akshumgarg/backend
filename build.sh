#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate

# Create superuser (add this line)
echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(email='akshumgarg20@gmail.com').exists() or User.objects.create_superuser(email='akshumgarg20@gmail.com', password='akshum@123', name='Akshum')" | python manage.py shell
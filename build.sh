#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate

# Create superuser (add this line)
echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(username='akshum').exists() or User.objects.create_superuser('akshum', 'akshumgarg20@gmail.com', 'akshum@123')" | python manage.py shell
from django.db import migrations
from django.contrib.auth.hashers import make_password

def create_admin_user(apps, schema_editor):
    # Get the models
    User = apps.get_model('auth', 'User')
    UserRole = apps.get_model('profile_system', 'UserRole')
    
    # Create superuser if it doesn't exist
    if not User.objects.filter(username='admin').exists():
        # Create admin user
        admin_user = User.objects.create(
            username='admin',
            email='admin@gsez.com',
            password=make_password('admin123'),  # Default password
            is_staff=True,
            is_superuser=True,
            first_name='Admin',
            last_name='User'
        )
        
        # Create admin role
        UserRole.objects.create(
            user=admin_user,
            role='admin',
            is_skip_profile=True
        )
        
        print("Admin user created successfully!")

def delete_admin_user(apps, schema_editor):
    # Get the models
    User = apps.get_model('auth', 'User')
    
    # Delete admin user if exists
    User.objects.filter(username='admin').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('profile_system', '0003_userrole_is_skip_profile'),
    ]

    operations = [
        migrations.RunPython(create_admin_user, delete_admin_user),
    ] 
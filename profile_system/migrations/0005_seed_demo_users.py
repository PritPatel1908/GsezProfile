from django.db import migrations
from django.contrib.auth.hashers import make_password
import datetime

def seed_demo_users(apps, schema_editor):
    # Get the models
    User = apps.get_model('auth', 'User')
    UserRole = apps.get_model('profile_system', 'UserRole')
    Profile = apps.get_model('profile_system', 'Profile')
    
    # Create demo users if they don't exist
    if not User.objects.filter(username='hr_user').exists():
        # Create HR user
        hr_user = User.objects.create(
            username='hr_user',
            email='hr@gsez.com',
            password=make_password('hr123'),  # Default password
            is_staff=False,
            is_superuser=False,
            first_name='HR',
            last_name='Manager'
        )
        
        # Create HR role
        UserRole.objects.create(
            user=hr_user,
            role='hr',
            is_skip_profile=False
        )
        
        # Create HR profile
        Profile.objects.create(
            user=hr_user,
            gsez_id='GSEZ-HR001',
            nationality='Gabon',
            date_of_birth=datetime.date(1985, 5, 15),
            expiry_date=datetime.date(2030, 12, 31),
            govt_id_number='HR12345678',
            emergency_contact='+241 77123456',
            status='active'
        )
    
    if not User.objects.filter(username='security_user').exists():
        # Create Security user
        security_user = User.objects.create(
            username='security_user',
            email='security@gsez.com',
            password=make_password('security123'),  # Default password
            is_staff=False,
            is_superuser=False,
            first_name='Security',
            last_name='Officer'
        )
        
        # Create Security role
        UserRole.objects.create(
            user=security_user,
            role='security',
            is_skip_profile=False
        )
        
        # Create Security profile
        Profile.objects.create(
            user=security_user,
            gsez_id='GSEZ-SEC001',
            nationality='Gabon',
            date_of_birth=datetime.date(1990, 8, 22),
            expiry_date=datetime.date(2030, 12, 31),
            govt_id_number='SEC87654321',
            emergency_contact='+241 77654321',
            status='active'
        )
    
    if not User.objects.filter(username='company_user').exists():
        # Create Company user
        company_user = User.objects.create(
            username='company_user',
            email='company@gsez.com',
            password=make_password('company123'),  # Default password
            is_staff=False,
            is_superuser=False,
            first_name='Company',
            last_name='Representative'
        )
        
        # Create Company role
        UserRole.objects.create(
            user=company_user,
            role='company',
            is_skip_profile=False
        )
        
        # Create Company profile
        Profile.objects.create(
            user=company_user,
            gsez_id='GSEZ-COM001',
            nationality='Gabon',
            date_of_birth=datetime.date(1982, 3, 10),
            expiry_date=datetime.date(2030, 12, 31),
            govt_id_number='COM24681012',
            emergency_contact='+241 77246810',
            status='active'
        )
    
    if not User.objects.filter(username='regular_user').exists():
        # Create Regular user
        regular_user = User.objects.create(
            username='regular_user',
            email='user@gsez.com',
            password=make_password('user123'),  # Default password
            is_staff=False,
            is_superuser=False,
            first_name='Regular',
            last_name='User'
        )
        
        # Create Regular user role
        UserRole.objects.create(
            user=regular_user,
            role='user',
            is_skip_profile=False
        )
        
        # Create Regular user profile
        Profile.objects.create(
            user=regular_user,
            gsez_id='GSEZ-USR001',
            nationality='Gabon',
            date_of_birth=datetime.date(1995, 11, 5),
            expiry_date=datetime.date(2030, 12, 31),
            govt_id_number='USR13579246',
            emergency_contact='+241 77135792',
            status='active'
        )
        
        print("Demo users seeded successfully!")

def delete_demo_users(apps, schema_editor):
    # Get the models
    User = apps.get_model('auth', 'User')
    
    # Delete demo users if they exist
    User.objects.filter(username__in=['hr_user', 'security_user', 'company_user', 'regular_user']).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('profile_system', '0004_seed_initial_data'),
    ]

    operations = [
        migrations.RunPython(seed_demo_users, delete_demo_users),
    ] 
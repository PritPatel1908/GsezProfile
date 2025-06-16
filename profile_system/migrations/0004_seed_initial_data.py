from django.db import migrations
from django.utils import timezone
import datetime

def seed_initial_data(apps, schema_editor):
    # Get the models
    Company = apps.get_model('profile_system', 'Company')
    JobPosting = apps.get_model('profile_system', 'JobPosting')
    
    # Create companies if they don't exist
    if not Company.objects.exists():
        # Create companies
        company1 = Company.objects.create(
            name='GSEZ Technologies',
            registration_number='GSEZ-TECH-001',
            address='GSEZ Technology Park, Block A, Gabon',
            contact_email='info@gseztech.com',
            contact_phone='+241 74123456',
            website='https://gseztech.com'
        )
        
        company2 = Company.objects.create(
            name='GSEZ Manufacturing',
            registration_number='GSEZ-MFG-002',
            address='GSEZ Industrial Zone, Block B, Gabon',
            contact_email='info@gsezmfg.com',
            contact_phone='+241 74789012',
            website='https://gsezmfg.com'
        )
        
        company3 = Company.objects.create(
            name='GSEZ Logistics',
            registration_number='GSEZ-LOG-003',
            address='GSEZ Port Area, Block C, Gabon',
            contact_email='info@gsezlog.com',
            contact_phone='+241 74345678',
            website='https://gsezlog.com'
        )
        
        # Create job postings
        closing_date = timezone.now().date() + datetime.timedelta(days=30)
        
        JobPosting.objects.create(
            company=company1,
            title='Software Developer',
            description='We are looking for experienced software developers to join our team.',
            requirements='Bachelor\'s degree in Computer Science, 3+ years of experience in web development.',
            location='GSEZ Technology Park',
            salary_range='$3000-$5000',
            closing_date=closing_date,
            is_active=True
        )
        
        JobPosting.objects.create(
            company=company2,
            title='Production Manager',
            description='Responsible for overseeing manufacturing operations.',
            requirements='Bachelor\'s degree in Engineering, 5+ years of experience in manufacturing.',
            location='GSEZ Industrial Zone',
            salary_range='$4000-$6000',
            closing_date=closing_date,
            is_active=True
        )
        
        JobPosting.objects.create(
            company=company3,
            title='Logistics Coordinator',
            description='Coordinate logistics operations and manage supply chain.',
            requirements='Bachelor\'s degree in Logistics, 2+ years of experience in logistics management.',
            location='GSEZ Port Area',
            salary_range='$2500-$4000',
            closing_date=closing_date,
            is_active=True
        )
        
        print("Initial data seeded successfully!")

def delete_initial_data(apps, schema_editor):
    # Get the models
    Company = apps.get_model('profile_system', 'Company')
    JobPosting = apps.get_model('profile_system', 'JobPosting')
    
    # Delete all job postings and companies
    JobPosting.objects.all().delete()
    Company.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('profile_system', '0003_create_admin_user'),
    ]

    operations = [
        migrations.RunPython(seed_initial_data, delete_initial_data),
    ] 
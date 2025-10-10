from django.core.management.base import BaseCommand
from django.db import transaction
from dashboard.models import JobPortal

class Command(BaseCommand):
    help = 'Initialize all required job portals in the database'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Initializing job portals...'))
        
        # List of all 36 required job portals
        portals = [
            # UK & USA Major Job Portals
            {'name': 'Indeed UK', 'url': 'https://www.indeed.co.uk/', 'is_active': True},
            {'name': 'LinkedIn Jobs', 'url': 'https://www.linkedin.com/jobs/', 'is_active': True},
            {'name': 'CV-Library', 'url': 'https://www.cv-library.co.uk/', 'is_active': True},
            {'name': 'Adzuna', 'url': 'https://www.adzuna.co.uk/', 'is_active': True},
            {'name': 'Totaljobs', 'url': 'https://www.totaljobs.com/', 'is_active': True},
            {'name': 'Reed', 'url': 'https://www.reed.co.uk/', 'is_active': True},
            {'name': 'Talent', 'url': 'https://www.talent.com/', 'is_active': True},
            {'name': 'Glassdoor', 'url': 'https://www.glassdoor.com/', 'is_active': True},
            {'name': 'ZipRecruiter', 'url': 'https://www.ziprecruiter.com/', 'is_active': True},
            {'name': 'CWjobs', 'url': 'https://www.cwjobs.co.uk/', 'is_active': True},
            {'name': 'Jobsora', 'url': 'https://uk.jobsora.com/', 'is_active': True},
            {'name': 'WelcometotheJungle', 'url': 'https://www.welcometothejungle.com/en/jobs', 'is_active': True},
            {'name': 'IT Job Board', 'url': 'https://www.technojobs.co.uk/', 'is_active': True},
            {'name': 'Trueup', 'url': 'https://www.trueup.io/', 'is_active': True},
            {'name': 'Redefined', 'url': 'https://redefined.jobs/', 'is_active': True},
            
            # Remote Work Portals
            {'name': 'We Work Remotely', 'url': 'https://weworkremotely.com/', 'is_active': True},
            {'name': 'AngelList', 'url': 'https://angel.co/jobs', 'is_active': True},
            {'name': 'Jobspresso', 'url': 'https://jobspresso.co/', 'is_active': True},
            {'name': 'Grabjobs', 'url': 'https://grabjobs.co/', 'is_active': True},
            {'name': 'Remote OK', 'url': 'https://remoteok.com/', 'is_active': True},
            {'name': 'Working Nomads', 'url': 'https://www.workingnomads.co/jobs', 'is_active': True},
            {'name': 'WorkInStartups', 'url': 'https://workinstartups.com/', 'is_active': True},
            {'name': 'Jobtensor', 'url': 'https://jobtensor.com/', 'is_active': True},
            {'name': 'Jora', 'url': 'https://www.jora.com/', 'is_active': True},
            {'name': 'SEOJobs.com', 'url': 'https://www.seojobs.com/', 'is_active': True},
            
            # Additional US-focused Portals
            {'name': 'CareerBuilder', 'url': 'https://www.careerbuilder.com/', 'is_active': True},
            {'name': 'Dice', 'url': 'https://www.dice.com/', 'is_active': True},
            {'name': 'Escape The City', 'url': 'https://www.escapethecity.org/', 'is_active': True},
            {'name': 'Jooble', 'url': 'https://jooble.org/', 'is_active': True},
            {'name': 'Otta', 'url': 'https://otta.com/', 'is_active': True},
            {'name': 'Remote.co', 'url': 'https://remote.co/remote-jobs/', 'is_active': True},
            {'name': 'SEL Jobs', 'url': 'https://jobs.searchenginejournal.com/', 'is_active': True},
            {'name': 'FlexJobs', 'url': 'https://www.flexjobs.com/', 'is_active': True},
            {'name': 'Dynamite Jobs', 'url': 'https://dynamitejobs.com/', 'is_active': True},
            {'name': 'SimplyHired', 'url': 'https://www.simplyhired.com/', 'is_active': True},
            {'name': 'Remotive', 'url': 'https://remotive.io/', 'is_active': True},
        ]
        
        count_created = 0
        count_updated = 0
        
        # Batch create or update job portals
        with transaction.atomic():
            for portal_data in portals:
                portal, created = JobPortal.objects.update_or_create(
                    name=portal_data['name'],
                    defaults={
                        'url': portal_data['url'],
                        'is_active': portal_data['is_active']
                    }
                )
                
                if created:
                    count_created += 1
                else:
                    count_updated += 1
        
        self.stdout.write(self.style.SUCCESS(
            f'Successfully initialized job portals:'
            f'\n- Created: {count_created}'
            f'\n- Updated: {count_updated}'
            f'\n- Total: {count_created + count_updated}'
        ))
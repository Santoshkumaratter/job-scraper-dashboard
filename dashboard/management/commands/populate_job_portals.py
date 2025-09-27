from django.core.management.base import BaseCommand
from dashboard.models import JobPortal

class Command(BaseCommand):
    help = 'Populate job portals in the database'

    def handle(self, *args, **options):
        # All job portals as per client requirements
        job_portals = [
            {'name': 'Indeed UK', 'url': 'https://uk.indeed.com'},
            {'name': 'LinkedIn Jobs', 'url': 'https://www.linkedin.com/jobs'},
            {'name': 'CV-Library', 'url': 'https://www.cv-library.co.uk'},
            {'name': 'Adzuna', 'url': 'https://www.adzuna.com'},
            {'name': 'Totaljobs', 'url': 'https://www.totaljobs.com'},
            {'name': 'Reed', 'url': 'https://www.reed.co.uk'},
            {'name': 'Talent', 'url': 'https://www.talent.com'},
            {'name': 'Glassdoor', 'url': 'https://www.glassdoor.com'},
            {'name': 'ZipRecruiter', 'url': 'https://www.ziprecruiter.com'},
            {'name': 'CWjobs', 'url': 'https://www.cwjobs.co.uk'},
            {'name': 'Jobsora', 'url': 'https://jobsora.com'},
            {'name': 'WelcometotheJungle', 'url': 'https://www.welcometothejungle.com'},
            {'name': 'IT Job Board', 'url': 'https://www.itjobboard.co.uk'},
            {'name': 'Trueup', 'url': 'https://www.trueup.io'},
            {'name': 'Redefined', 'url': 'https://www.redefined.co.uk'},
            {'name': 'We Work Remotely', 'url': 'https://weworkremotely.com'},
            {'name': 'AngelList', 'url': 'https://angel.co'},
            {'name': 'Jobspresso', 'url': 'https://jobspresso.co'},
            {'name': 'Grabjobs', 'url': 'https://www.grabjobs.co.uk'},
            {'name': 'Remote OK', 'url': 'https://remoteok.io'},
            {'name': 'Working Nomads', 'url': 'https://www.workingnomads.com'},
            {'name': 'WorkInStartups', 'url': 'https://www.workinstartups.com'},
            {'name': 'Jobtensor', 'url': 'https://www.jobtensor.com'},
            {'name': 'Jora', 'url': 'https://au.jora.com'},
            {'name': 'SEOJobs.com', 'url': 'https://www.seojobs.com'},
            {'name': 'CareerBuilder', 'url': 'https://www.careerbuilder.com'},
            {'name': 'Dice', 'url': 'https://www.dice.com'},
            {'name': 'Escape The City', 'url': 'https://www.escapethecity.org'},
            {'name': 'Jooble', 'url': 'https://jooble.org'},
            {'name': 'Otta', 'url': 'https://otta.com'},
            {'name': 'Remote.co', 'url': 'https://remote.co'},
            {'name': 'SEL Jobs', 'url': 'https://www.seljobs.com'},
            {'name': 'FlexJobs', 'url': 'https://www.flexjobs.com'},
            {'name': 'Dynamite Jobs', 'url': 'https://dynamitejobs.com'},
            {'name': 'SimplyHired', 'url': 'https://www.simplyhired.com'},
            {'name': 'Remotive', 'url': 'https://remotive.com'},
        ]

        created_count = 0
        updated_count = 0

        for portal_data in job_portals:
            portal, created = JobPortal.objects.get_or_create(
                name=portal_data['name'],
                defaults={
                    'url': portal_data['url'],
                    'is_active': True
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created: {portal.name}')
                )
            else:
                # Update URL if it changed
                if portal.url != portal_data['url']:
                    portal.url = portal_data['url']
                    portal.is_active = True
                    portal.save()
                    updated_count += 1
                    self.stdout.write(
                        self.style.WARNING(f'Updated: {portal.name}')
                    )

        self.stdout.write(
            self.style.SUCCESS(
                f'\n✅ Job portals populated successfully!\n'
                f'Created: {created_count}\n'
                f'Updated: {updated_count}\n'
                f'Total: {JobPortal.objects.count()}'
            )
        )

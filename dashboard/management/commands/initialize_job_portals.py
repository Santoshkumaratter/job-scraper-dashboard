#!/usr/bin/env python
"""
Management command to initialize all job portals in the database
"""

from django.core.management.base import BaseCommand
from dashboard.models import JobPortal


class Command(BaseCommand):
    help = 'Initialize all job portals in the database'

    def handle(self, *args, **options):
        # All job portals as per client requirements
        job_portals = {
            'Indeed UK': 'https://uk.indeed.com',
            'Indeed US': 'https://www.indeed.com',
            'LinkedIn Jobs': 'https://www.linkedin.com/jobs',
            'CV-Library': 'https://www.cv-library.co.uk',
            'Adzuna': 'https://www.adzuna.com',
            'Totaljobs': 'https://www.totaljobs.com',
            'Reed': 'https://www.reed.co.uk',
            'Talent': 'https://www.talent.com',
            'Glassdoor': 'https://www.glassdoor.com',
            'ZipRecruiter': 'https://www.ziprecruiter.com',
            'CWjobs': 'https://www.cwjobs.co.uk',
            'Jobsora': 'https://jobsora.com',
            'WelcometotheJungle': 'https://www.welcometothejungle.com',
            'IT Job Board': 'https://www.itjobboard.co.uk',
            'Trueup': 'https://www.trueup.io',
            'Redefined': 'https://www.redefined.co.uk',
            'We Work Remotely': 'https://weworkremotely.com',
            'AngelList': 'https://angel.co',
            'Jobspresso': 'https://jobspresso.co',
            'Grabjobs': 'https://www.grabjobs.co.uk',
            'Remote OK': 'https://remoteok.io',
            'Working Nomads': 'https://www.workingnomads.com',
            'WorkInStartups': 'https://www.workinstartups.com',
            'Jobtensor': 'https://www.jobtensor.com',
            'Jora': 'https://au.jora.com',
            'SEOJobs.com': 'https://www.seojobs.com',
            'CareerBuilder': 'https://www.careerbuilder.com',
            'Dice': 'https://www.dice.com',
            'Escape The City': 'https://www.escapethecity.org',
            'Jooble': 'https://jooble.org',
            'Otta': 'https://otta.com',
            'Remote.co': 'https://remote.co',
            'SEL Jobs': 'https://www.seljobs.com',
            'FlexJobs': 'https://www.flexjobs.com',
            'Dynamite Jobs': 'https://dynamitejobs.com',
            'SimplyHired': 'https://www.simplyhired.com',
            'Remotive': 'https://remotive.com',
        }
        
        created_count = 0
        updated_count = 0
        
        for portal_name, portal_url in job_portals.items():
            portal, created = JobPortal.objects.get_or_create(
                name=portal_name,
                defaults={'url': portal_url, 'is_active': True}
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created: {portal_name}')
                )
            else:
                # Update URL if it changed
                if portal.url != portal_url:
                    portal.url = portal_url
                    portal.is_active = True
                    portal.save()
                    updated_count += 1
                    self.stdout.write(
                        self.style.WARNING(f'Updated: {portal_name}')
                    )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\nJob portals initialization completed!\n'
                f'Created: {created_count}\n'
                f'Updated: {updated_count}\n'
                f'Total: {len(job_portals)}'
            )
        )

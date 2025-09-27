from django.core.management.base import BaseCommand
from dashboard.models import JobListing, Company, DecisionMaker


class Command(BaseCommand):
    help = 'Test delete functionality'

    def handle(self, *args, **options):
        # Show current data
        jobs_count = JobListing.objects.count()
        companies_count = Company.objects.count()
        decision_makers_count = DecisionMaker.objects.count()
        
        self.stdout.write(f"Before delete:")
        self.stdout.write(f"  Jobs: {jobs_count}")
        self.stdout.write(f"  Companies: {companies_count}")
        self.stdout.write(f"  Decision Makers: {decision_makers_count}")
        
        if jobs_count > 0:
            # Test single job delete
            first_job = JobListing.objects.first()
            self.stdout.write(f"\nTesting single job delete...")
            self.stdout.write(f"  Deleting job: {first_job.job_title} (ID: {first_job.id})")
            first_job.delete()
            
            # Show results
            jobs_after = JobListing.objects.count()
            self.stdout.write(f"  Jobs after delete: {jobs_after}")
            
            if jobs_after > 0:
                self.stdout.write(f"\nTesting delete all...")
                # Delete all remaining data
                JobListing.objects.all().delete()
                DecisionMaker.objects.all().delete()
                Company.objects.all().delete()
                
                jobs_final = JobListing.objects.count()
                companies_final = Company.objects.count()
                decision_makers_final = DecisionMaker.objects.count()
                
                self.stdout.write(f"After delete all:")
                self.stdout.write(f"  Jobs: {jobs_final}")
                self.stdout.write(f"  Companies: {companies_final}")
                self.stdout.write(f"  Decision Makers: {decision_makers_final}")
                
                if jobs_final == 0 and companies_final == 0 and decision_makers_final == 0:
                    self.stdout.write(self.style.SUCCESS("✅ Delete functionality working correctly!"))
                else:
                    self.stdout.write(self.style.ERROR("❌ Delete functionality not working properly"))
            else:
                self.stdout.write(self.style.SUCCESS("✅ Single job delete working correctly!"))
        else:
            self.stdout.write(self.style.WARNING("No jobs to test delete functionality"))

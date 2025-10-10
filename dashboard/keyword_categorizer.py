"""
Keyword Categorizer for Job Scraper
Helps categorize jobs as technical or non-technical based on keywords
"""

import re
from typing import List, Dict, Tuple, Any

class KeywordCategorizer:
    """
    Categorizes job titles and keywords as technical or non-technical
    based on predefined sets of technical and non-technical terms.
    """
    
    def __init__(self):
        """Initialize with technical and non-technical keyword sets"""
        # Technical job title keywords
        self.technical_keywords = {
            # Programming languages
            'python', 'java', 'javascript', 'typescript', 'c#', 'c++', 'ruby', 'php',
            'golang', 'go', 'rust', 'swift', 'kotlin', 'scala', 'perl', 'r language',
            'dart', 'flutter', 'objective-c', 'shell', 'powershell', 'bash', 'sql',
            'html', 'css', 'sass', 'less', 'xml', 'json', 'yaml',
            
            # Development roles
            'developer', 'software engineer', 'programmer', 'coder', 'software developer',
            'web developer', 'front-end', 'frontend', 'back-end', 'backend',
            'full-stack', 'full stack', 'mobile developer', 'ios developer',
            'android developer', 'game developer', 'app developer',
            'software architect', 'solutions architect',
            
            # Technical disciplines
            'devops', 'sre', 'site reliability', 'devsecops', 'cloud engineer',
            'database', 'dba', 'data engineer', 'data scientist', 'data analyst',
            'machine learning', 'ml', 'ai engineer', 'nlp', 'computer vision',
            'data mining', 'big data', 'etl developer', 'hadoop', 'spark',
            'qa engineer', 'quality assurance', 'automation', 'test engineer',
            'security engineer', 'infosec', 'cybersecurity', 'penetration tester',
            
            # Infrastructure
            'systems administrator', 'sysadmin', 'network administrator',
            'network engineer', 'cloud architect', 'aws', 'azure', 'gcp',
            'kubernetes', 'docker', 'terraform', 'ansible', 'chef', 'puppet',
            
            # Technical frameworks/libraries
            'react', 'angular', 'vue', 'node', 'express', 'django', 'flask', 'rails',
            'laravel', 'spring', 'hibernate', 'bootstrap', 'tailwind', 'jquery',
            'tensorflow', 'pytorch', 'keras', 'scikit-learn', 'pandas',
            
            # Technical job prefixes/suffixes
            'senior', 'staff', 'principal', 'lead', 'head of', 'director of',
            'engineer', 'engineering', 'technical', 'technology', 'development'
        }
        
        # Non-technical job title keywords
        self.non_technical_keywords = {
            # Marketing
            'marketing', 'seo', 'sem', 'content', 'social media', 'brand',
            'digital marketing', 'growth', 'acquisition', 'email marketing',
            'performance marketing', 'marketing automation', 'crm', 'inbound',
            
            # Sales & Business
            'sales', 'account', 'business development', 'account executive',
            'sales representative', 'account manager', 'customer success',
            'client manager', 'business analyst', 'sales operations',
            
            # Design (non-technical)
            'graphic design', 'ui design', 'ux design', 'product design',
            'visual design', 'web design', 'illustration', 'motion design',
            
            # Content & Communications
            'content writer', 'copywriter', 'editor', 'content strategist',
            'technical writer', 'communications', 'pr', 'public relations',
            'journalist', 'content creator',
            
            # HR & Recruitment
            'recruiter', 'talent acquisition', 'hr', 'human resources',
            'people operations', 'office manager', 'talent', 'recruiting',
            
            # Management & Operations
            'operations', 'project manager', 'product manager', 'program manager',
            'scrum master', 'agile coach', 'operations manager', 'delivery manager',
            
            # Finance & Legal
            'finance', 'accounting', 'legal', 'compliance', 'financial analyst',
            'controller', 'bookkeeper', 'paralegal',
            
            # Support & Services
            'customer support', 'customer service', 'help desk', 'technical support',
            'service desk', 'customer care', 'customer experience'
        }
        
    def categorize_job_title(self, job_title: str) -> Tuple[bool, float]:
        """
        Categorize a job title as technical or non-technical
        
        Args:
            job_title: The job title string to categorize
            
        Returns:
            Tuple of (is_technical, confidence_score)
        """
        job_title = job_title.lower()
        
        # Count keyword matches in both categories
        technical_matches = sum(1 for kw in self.technical_keywords if kw.lower() in job_title)
        non_technical_matches = sum(1 for kw in self.non_technical_keywords if kw.lower() in job_title)
        
        # Compute confidence score (0 to 1)
        if technical_matches > non_technical_matches:
            confidence = min(0.5 + (technical_matches - non_technical_matches) * 0.1, 1.0)
            return True, confidence
        elif non_technical_matches > technical_matches:
            confidence = min(0.5 + (non_technical_matches - technical_matches) * 0.1, 1.0)
            return False, confidence
        
        # If tied, use some heuristics for common job titles
        if any(role in job_title for role in ['developer', 'engineer', 'programmer', 'devops']):
            return True, 0.8
        elif any(role in job_title for role in ['marketing', 'sales', 'manager', 'coordinator']):
            return False, 0.8
            
        # Default: assume technical with low confidence
        return True, 0.55
        
    def categorize_job_description(self, description: str) -> Tuple[bool, float]:
        """
        Categorize job based on description text
        
        Args:
            description: The job description text
            
        Returns:
            Tuple of (is_technical, confidence_score)
        """
        if not description:
            return True, 0.5  # Default with low confidence
            
        description = description.lower()
        
        # Count keyword matches in both categories
        technical_matches = sum(1 for kw in self.technical_keywords if kw.lower() in description)
        non_technical_matches = sum(1 for kw in self.non_technical_keywords if kw.lower() in description)
        
        # Technical skills are often mentioned as requirements
        technical_skill_patterns = [
            r'(proficient|experience|skilled|knowledge)\s+in\s+([^\.]+)(python|java|javascript|sql)',
            r'(aws|azure|cloud)\s+experience',
            r'programming\s+(skills|experience)',
            r'(front|back)[\s-]end\s+development',
            r'database\s+(design|administration)',
            r'software\s+development\s+lifecycle'
        ]
        
        technical_requirements_count = sum(1 for pattern in technical_skill_patterns 
                                          if re.search(pattern, description, re.I))
        
        # Adjust scores based on requirements
        technical_matches += technical_requirements_count
        
        # Compute confidence score (0 to 1)
        if technical_matches > non_technical_matches:
            confidence = min(0.6 + (technical_matches - non_technical_matches) * 0.05, 1.0)
            return True, confidence
        elif non_technical_matches > technical_matches:
            confidence = min(0.6 + (non_technical_matches - technical_matches) * 0.05, 1.0)
            return False, confidence
            
        # If tied, default to technical with low confidence
        return True, 0.5
        
    def categorize_job(self, job_title: str, description: str = None) -> Tuple[bool, float]:
        """
        Categorize job based on both title and description
        
        Args:
            job_title: The job title
            description: Optional job description
            
        Returns:
            Tuple of (is_technical, confidence_score)
        """
        # Get categorizations from title and description
        title_technical, title_confidence = self.categorize_job_title(job_title)
        
        if description:
            desc_technical, desc_confidence = self.categorize_job_description(description)
            
            # Weighted average of confidences
            if title_technical == desc_technical:
                # If both agree, higher confidence
                is_technical = title_technical
                confidence = (title_confidence * 0.6) + (desc_confidence * 0.4)
            else:
                # If they disagree, use the one with higher confidence
                if title_confidence > desc_confidence:
                    is_technical = title_technical
                    confidence = title_confidence * 0.8  # Reduce confidence due to disagreement
                else:
                    is_technical = desc_technical
                    confidence = desc_confidence * 0.7  # Reduce confidence due to disagreement
        else:
            # Only title available
            is_technical = title_technical
            confidence = title_confidence
            
        return is_technical, confidence
        
    def get_suggested_keywords(self, is_technical: bool = True) -> List[str]:
        """
        Get suggested keywords for search based on technical category
        
        Args:
            is_technical: Whether to return technical or non-technical keywords
            
        Returns:
            List of suggested keywords
        """
        if is_technical:
            return [
                'Software Engineer', 'Full Stack Developer', 'Python Developer',
                'JavaScript Developer', 'Frontend Developer', 'Backend Developer',
                'DevOps Engineer', 'Data Scientist', 'Machine Learning Engineer',
                'Cloud Engineer', 'React Developer', 'Java Developer',
                'QA Engineer', 'Web Developer', 'Mobile Developer'
            ]
        else:
            return [
                'Marketing Manager', 'SEO Specialist', 'Digital Marketing',
                'Content Writer', 'Social Media Manager', 'Sales Representative',
                'Account Manager', 'Business Analyst', 'Product Manager',
                'Customer Success Manager', 'HR Specialist', 'Recruiter',
                'UX Designer', 'UI Designer', 'Operations Manager'
            ]
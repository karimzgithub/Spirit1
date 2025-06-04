from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator

class CrimeRecord(models.Model):
    """
    This model represents a crime record in the system.
    It stores all information related to a crime case including victim details,
    suspect information, evidence, and investigating officer details.
    """

    # Predefined choices for crime types to maintain consistency
    CRIME_TYPES = [
        ('THEFT', 'Theft'),
        ('ASSAULT', 'Assault'),
        ('BURGLARY', 'Burglary'),
        ('FRAUD', 'Fraud'),
        ('OTHER', 'Other'),
    ]

    # Possible statuses for a crime case
    STATUS_CHOICES = [
        ('OPEN', 'Open'),                    # Case is newly filed
        ('UNDER_INVESTIGATION', 'Under Investigation'),  # Case is being investigated
        ('CLOSED', 'Closed'),                # Case has been resolved
    ]

    # Phone number validation - ensures exactly 10 digits
    phone_validator = RegexValidator(
        regex=r'^\d{10}$',
        message='Phone number must be exactly 10 digits.'
    )

    # ===== Basic Information Section =====
    # Unique identifier for the case
    case_number = models.CharField(max_length=50, unique=True, help_text="Unique case number for the crime record")
    # Type of crime committed
    crime_type = models.CharField(max_length=20, choices=CRIME_TYPES)
    # Detailed description of the crime
    description = models.TextField()
    # Where the crime occurred
    location = models.CharField(max_length=200)
    # When the crime was reported to authorities
    date_reported = models.DateTimeField(default=timezone.now)
    # When the crime actually occurred
    date_occurred = models.DateTimeField()
    # Current status of the case
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='OPEN')

    # ===== Case Registration Details =====
    # First Information Report number (FIR)
    fir_number = models.CharField(max_length=50, unique=True, null=True, blank=True)
    # Date when FIR was filed
    fir_date = models.DateField(null=True, blank=True)
    # Court case number if case goes to trial
    court_case_number = models.CharField(max_length=50, unique=True, null=True, blank=True)

    # ===== Victim Details Section =====
    # Personal information about the victim
    victim_name = models.CharField(max_length=100)
    victim_age = models.PositiveIntegerField(null=False, blank=False)
    victim_gender = models.CharField(max_length=10, choices=[
        ('MALE', 'Male'),
        ('FEMALE', 'Female'),
        ('OTHER', 'Other'),
    ], null=False, blank=False)
    # Contact information with 10-digit validation
    victim_contact = models.CharField(max_length=15, null=False, blank=False, validators=[phone_validator])
    victim_address = models.TextField(null=False, blank=False)
    # Optional victim information
    victim_occupation = models.CharField(max_length=100, blank=True)
    victim_marital_status = models.CharField(max_length=20, choices=[
        ('SINGLE', 'Single'),
        ('MARRIED', 'Married'),
        ('DIVORCED', 'Divorced'),
        ('WIDOWED', 'Widowed'),
        ('OTHER', 'Other'),
    ], blank=True)

    # ===== Suspect Details Section =====
    # Required suspect information
    suspect_name = models.CharField(max_length=100, null=False, blank=False)
    # Optional suspect information
    suspect_age = models.PositiveIntegerField(null=True, blank=True)
    suspect_gender = models.CharField(max_length=10, choices=[
        ('MALE', 'Male'),
        ('FEMALE', 'Female'),
        ('OTHER', 'Other'),
    ], blank=True)
    suspect_contact = models.CharField(max_length=15, blank=True)
    suspect_address = models.TextField(blank=True)
    suspect_occupation = models.CharField(max_length=100, blank=True)
    # Current status of the suspect
    suspect_status = models.CharField(max_length=20, choices=[
        ('ARRESTED', 'Arrested'),
        ('AT_LARGE', 'At Large'),
        ('KNOWN', 'Known'),
        ('UNKNOWN', 'Unknown'),
    ], null=False, blank=False)
    # Photo of the suspect if available
    suspect_image = models.ImageField(upload_to='suspect_images/', null=True, blank=True)

    # ===== Evidence Details Section =====
    # Type of evidence collected
    evidence_type = models.CharField(max_length=50, choices=[
        ('WEAPON', 'Weapon'),
        ('DOCUMENTS', 'Documents'),
        ('CCTV', 'CCTV Footage'),
        ('DNA', 'DNA Evidence'),
        ('FINGERPRINTS', 'Fingerprints'),
        ('PHYSICAL', 'Physical Evidence'),
        ('DIGITAL', 'Digital Evidence'),
        ('BIOLOGICAL', 'Biological Evidence'),
        ('TRACE', 'Trace Evidence'),
        ('OTHER', 'Other'),
    ], null=False, blank=False)
    # When the evidence was collected
    evidence_collection_date = models.DateField(null=True, blank=True)
    # Detailed description of the evidence
    evidence_description = models.TextField(null=True, blank=True)
    # Where the evidence is stored
    evidence_location = models.CharField(max_length=200, null=False, blank=False)
    # Chain of custody documentation
    evidence_chain_of_custody = models.TextField(blank=True)
    # Photo of the evidence if available
    evidence_image = models.ImageField(upload_to='evidence_images/', null=True, blank=True)

    # ===== Additional Information Section =====
    # General evidence notes
    evidence = models.TextField(blank=True)
    # Any additional notes about the case
    notes = models.TextField(blank=True)
    # Timestamps for record keeping
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # ===== Officer Details Section =====
    # Information about the investigating officer
    officer_name = models.CharField(max_length=100, null=False, blank=False)
    officer_badge = models.CharField(max_length=50, null=False, blank=False)
    officer_department = models.CharField(max_length=100, null=False, blank=False)
    # Contact information with 10-digit validation
    officer_contact = models.CharField(max_length=20, null=False, blank=False, validators=[phone_validator])

    def __str__(self):
        """
        Returns a string representation of the crime record.
        Format: "Case Number - Crime Type"
        """
        return f"{self.case_number} - {self.crime_type}"

    class Meta:
        """
        Meta class for CrimeRecord model.
        Orders records by date reported in descending order (newest first).
        """
        ordering = ['-date_reported']

    def clean(self):
        """
        Custom validation method to ensure case number uniqueness.
        Raises ValidationError if case number already exists.
        """
        super().clean()
        if CrimeRecord.objects.filter(case_number=self.case_number).exclude(pk=self.pk).exists():
            raise ValidationError({'case_number': 'This case number is already in use.'})

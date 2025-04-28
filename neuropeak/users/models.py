from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager, PermissionsMixin
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('user_type', User.UserType.SUPERUSER)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self.create_user(email, password, **extra_fields)

class User(AbstractUser, PermissionsMixin):
    class UserType(models.TextChoices):
        SUPERUSER = 'SUPERUSER', 'Superuser'
        LECTURER = 'LECTURER', 'Lecturer'
        STUDENT = 'STUDENT', 'Student'

    username = None
    email = models.EmailField(_('email address'), unique=True)
    user_type = models.CharField(
        max_length=10,
        choices=UserType.choices,
        default=UserType.STUDENT
    )
    
    # Common fields for all user types
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    
    # Lecturer-specific fields (nullable)
    department = models.CharField(max_length=100, blank=True, null=True)
    specialization = models.CharField(max_length=100, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    
    # Student-specific fields (nullable)
    # student_id = models.CharField(max_length=20, unique=True, blank=True, null=True)
    program = models.CharField(max_length=100, blank=True, null=True)
    year_of_study = models.PositiveIntegerField(blank=True, null=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    objects = UserManager()

    # Add these to resolve the clashes
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        related_name="custom_user_groups",
        related_query_name="custom_user",
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name="custom_user_permissions",
        related_query_name="custom_user",
    )

    def __str__(self):
        return self.email
    
    def clean(self):
        super().clean()
        self.clean_user_type_fields()
        
        # Additional validation
        if self.user_type == self.UserType.LECTURER and not self.department:
            raise ValidationError({'department': 'Department is required for lecturers'})
        # if self.user_type == self.UserType.STUDENT and not self.student_id:
        #     raise ValidationError({'student_id': 'Student ID is required for students'})

    def clean_user_type_fields(self):
        """Clean up fields based on user type"""
        if self.is_superuser:
            self.user_type = self.UserType.SUPERUSER
        
        if self.user_type != self.UserType.LECTURER:
            self.department = None
            self.specialization = None
            self.bio = None
            
        if self.user_type != self.UserType.STUDENT:
            # self.student_id = None
            self.program = None
            self.year_of_study = None

    @property
    def is_lecturer(self):
        return self.user_type == self.UserType.LECTURER
    
    @property
    def is_student(self):
        return self.user_type == self.UserType.STUDENT
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

@receiver(pre_save, sender=User)
def user_pre_save(sender, instance, **kwargs):
    instance.clean_user_type_fields()

class LecturerProfile(models.Model):
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE,
        limit_choices_to={'user_type': User.UserType.LECTURER}
    )
    department = models.CharField(max_length=100)
    specialization = models.CharField(max_length=100)
    bio = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.user.email} - {self.department}"

class StudentProfile(models.Model):
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE,
        limit_choices_to={'user_type': User.UserType.STUDENT}
    )
    # student_id = models.CharField(max_length=20, unique=True)
    program = models.CharField(max_length=100)
    year_of_study = models.PositiveIntegerField()
    
    def __str__(self):
        return f"{self.user.email} - {self.program}"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        if instance.user_type == User.UserType.LECTURER:
            LecturerProfile.objects.create(
                user=instance,
                department=instance.department or '',
                specialization=instance.specialization or '',
                bio=instance.bio or ''
            )
        elif instance.user_type == User.UserType.STUDENT:
            StudentProfile.objects.create(
                user=instance,
                # student_id=instance.student_id,
                program=instance.program or '',
                year_of_study=instance.year_of_study or 1
            )
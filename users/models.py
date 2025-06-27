from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserProfile(models.Model):
    """
    Extended user profile model with additional user information.
    
    Attributes:
        user: OneToOne relationship with Django's User model
        bio: Optional biography text
        phone_number: Optional phone number
        date_of_birth: Optional date of birth
        created_at: Timestamp when profile was created
        updated_at: Timestamp when profile was last updated
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=500, blank=True, help_text="Tell us about yourself")
    phone_number = models.CharField(max_length=15, blank=True, help_text="Contact phone number")
    date_of_birth = models.DateField(null=True, blank=True, help_text="Your date of birth")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        """Return string representation of UserProfile."""
        return f"{self.user.username}'s Profile"

    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create UserProfile when a new User is created."""
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Save UserProfile when User is saved."""
    instance.userprofile.save()

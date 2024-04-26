from django.db import models


class RegisteredUser(models.Model):
    user_id = models.IntegerField(primary_key=True)
    email = models.EmailField(max_length=255, unique=True)
    email_confirmed = models.BooleanField(default=False)
    developer_mode = models.BooleanField(default=False)  # New field for developer mode

    def __str__(self):
        developer_status = 'Enabled' if self.developer_mode else 'Disabled'
        return (f"{self.user_id} - {self.email} - {'Confirmed' if self.email_confirmed else 'Not Confirmed'}"
                f" - Developer Mode: {developer_status}")

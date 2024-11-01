from django.db import models


class UserSignup(models.Model):
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)

    def __str__(self):
        return self.username

    def save(self, *args, **kwargs):
        # Add any additional processing before saving or validations here
        super(UserSignup, self).save(*args, **kwargs)


if __name__ == "__main__":
    print("Django UserSignup Model ready!")

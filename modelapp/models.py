from django.db import models

# Create your models here.

class Model(models.Model):
    question = models.TextField()
    answer = models.TextField()
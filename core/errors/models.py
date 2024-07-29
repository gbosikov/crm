from django.db import models


class Errors(models.Model):
    error_code = models.IntegerField(default=None)
    error_lang = models.CharField(max_length=150)  #eng, geo
    error_text_eng = models.TextField()
    error_text_geo = models.TextField()

    def __str__(self):
        return self.error_code

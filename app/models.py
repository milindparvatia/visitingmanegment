from django.db import models

class Host(models.Model):
    full_name = models.CharField(max_length=30)
    email = models.EmailField(max_length=20)
    mobile = models.IntegerField()
    comment = models.CharField(max_length=100, null=True)

    def __str__(self):
        return self.full_name

class Visitor(models.Model):
    full_name = models.CharField(max_length=30)
    company_name = models.CharField(max_length=20)
    email = models.EmailField(max_length=20)
    mobile = models.IntegerField()
    licenseplate = models.IntegerField(null=True)
    about = models.CharField(max_length=50, null=True)
    comment = models.CharField(max_length=100, null=True)
    visiting = models.ManyToManyField(Host, through='Visit', related_name='relateds')

    def __str__(self):
        return self.full_name    

class Visit(models.Model):
    visitor = models.ForeignKey(Visitor, on_delete=models.CASCADE)
    host = models.ForeignKey(Host, on_delete=models.CASCADE)
    visit = models.DateField()
    invite_reason = models.CharField(max_length=64, null=True)
from django.db import models

class User(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=100)
    def __str__(self):
        return self.name

class AdCampaign(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product_name = models.CharField(max_length=200)
    budget = models.FloatField()
    target_audience = models.CharField(max_length=500)
    industry = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()
    def __str__(self):
        return f"{self.product_name} ({self.user.name})"

class AdPerformance(models.Model):
    platform = models.CharField(max_length=50)  # Google, Facebook, etc.
    campaign = models.ForeignKey(AdCampaign, on_delete=models.CASCADE)
    spend = models.FloatField()
    reach = models.IntegerField()
    impressions = models.IntegerField()
    clicks = models.IntegerField()
    date = models.DateField(auto_now_add=True)
    def __str__(self):
        return f"{self.platform} | {self.campaign.product_name} | {self.date}"


class AdPlatformData(models.Model):
    platform = models.CharField(max_length=100)
    budget = models.FloatField()
    impressions = models.IntegerField()
    clicks = models.IntegerField()
    cost_per_click = models.FloatField()
    reach = models.IntegerField()

    def __str__(self):
        return f"{self.platform} - ₹{self.budget}"

class AdCampaignHistory(models.Model):
    platform = models.CharField(max_length=100)
    budget = models.FloatField()
    reach = models.IntegerField()
    clicks = models.IntegerField()
    date = models.DateField(auto_now_add=True)
    def __str__(self):
        return f"{self.platform} - {self.date}"

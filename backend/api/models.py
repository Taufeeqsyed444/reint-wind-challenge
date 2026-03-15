from django.db import models

class ActualGeneration(models.Model):
    """Stores the actual wind generation from the FUELHH endpoint"""
    timestamp = models.DateTimeField(unique=True, db_index=True)
    generation_mw = models.FloatField()

    def __str__(self):
        return f"{self.timestamp} - {self.generation_mw} MW"

class ForecastGeneration(models.Model):
    """Stores the forecasted wind generation from the WINDFOR endpoint"""
    publish_time = models.DateTimeField(db_index=True)
    target_time = models.DateTimeField(db_index=True)
    generation_mw = models.FloatField()

    class Meta:
        # A forecast is unique for a specific publish time and target time
        unique_together = ('publish_time', 'target_time')

    def __str__(self):
        return f"Pub: {self.publish_time} -> Target: {self.target_time} | {self.generation_mw} MW"
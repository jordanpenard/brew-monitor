from datetime import datetime
from django.utils.timesince import timesince
from django.utils.timezone import make_aware
from django.db import models
from django.contrib.auth.models import User

class Sensor(models.Model):
    name = models.CharField(max_length=200)
    secret = models.CharField(max_length=200)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    max_battery = models.FloatField(default=4.0)
    min_battery = models.FloatField(default=2.0)

    def last_active(self):
        return self.datapoints.order_by("-timestamp").first().timestamp if self.datapoints.exists() else None

    def last_active_str(self):
        last = self.last_active()
        return last.isoformat() if last else "No data"

    def is_active(self):
        last = self.last_active()
        return last is not None and (make_aware(datetime.now()) - last).days < 1

    def last_battery_pct(self):
        last_dp = self.datapoints.order_by("-timestamp").first()
        if last_dp and self.max_battery is not None and self.min_battery is not None:
            if last_dp.battery > self.max_battery:
                return 100
            if last_dp.battery < self.min_battery:
                return 0
            return int(((last_dp.battery - self.min_battery) * 100) / (self.max_battery - self.min_battery))
        return None

    def battery_info(self):
        value = self.last_battery_pct()
        if value is None:
            label = 'Unknown battery state'
            icon = 'fa-question'
        else:
            label = f'{value}%'
            if value > 80:
                icon = 'fa-battery-full'
            elif value > 60:
                icon = 'fa-battery-three-quarters'
            elif value > 40:
                icon = 'fa-battery-half'
            elif value > 20:
                icon = 'fa-battery-quarter'
            else:
                icon = 'fa-battery-empty'
        return {
            'value': value,
            'tooltip': label,
            'icon': icon,
        }

    def __str__(self):
        return self.name

class Project(models.Model):
    name = models.CharField(max_length=200)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    active_sensor = models.OneToOneField(Sensor, on_delete=models.SET_NULL, null=True, blank=True, related_name='active_project')

    def first_active(self):
        data = Datapoint.objects.filter(project=self).order_by("timestamp").first()
        if data:
            return data.timestamp
        return None
    
    def last_active(self):
        data = Datapoint.objects.filter(project=self).order_by("-timestamp").first()
        if data:
            return data.timestamp
        return None
    
    def is_active(self):
        last = self.last_active()
        return last is not None and (make_aware(datetime.now()) - last).days < 1

    def first_angle(self):
        data = Datapoint.objects.filter(project=self).order_by("timestamp").first()
        if data:
            return data.angle
        return None

    def last_angle(self):
        data = Datapoint.objects.filter(project=self).order_by("-timestamp").first()
        if data:
            return data.angle
        return None
    
    def last_temperature(self):
        data = Datapoint.objects.filter(project=self).order_by("-timestamp").first()
        if data:
            return data.temperature
        return None

    def delta_angle(self):
        return self.last_angle() - self.first_angle()

    def length_active(self):
        delta = self.last_active() - self.first_active()
            
        total_seconds = int(abs(delta.total_seconds()))
        
        days, remainder = divmod(total_seconds, 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        time_str = f"{hours:02}:{minutes:02}:{seconds:02}"
        
        if days > 0:
            unit = "day" if days == 1 else "days"
            return f"{days} {unit}, {time_str}"
        
        return time_str

    def __str__(self):
        return self.name

class Datapoint(models.Model):
    sensor = models.ForeignKey(Sensor, on_delete=models.CASCADE, related_name='datapoints')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='datapoints', null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    angle = models.FloatField()
    temperature = models.FloatField()
    battery = models.FloatField()

    def __str__(self):
        return f"{self.sensor.name} - {self.timestamp}"

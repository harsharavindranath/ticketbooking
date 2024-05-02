from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class CustomUser(AbstractUser):
    gender_choices=(('Female','Female'),
                    ('Male','Male'))
    fullname=models.CharField(max_length=20,null=False)
    age=models.IntegerField()
    gender=models.CharField(max_length=20,choices=gender_choices,null=False)
    email=models.EmailField(max_length=255,null=False)
    password=models.CharField(max_length=100,null=False)

def _str_(self):
    return self.fullname


class Bus(models.Model):
    TYPE_CHOICES=[('AC','AC'),
                  ('Non AC Deluxe','Non AC Deluxe'),
                  ('Ordinary','Ordinary')]
    type=models.CharField(max_length=20,choices=TYPE_CHOICES,default='Ordinary')
    bus_name = models.CharField(max_length=30)
    source = models.CharField(max_length=30)
    destination = models.CharField(max_length=30)
    no_of_seat = models.IntegerField()
    rem_seat = models.IntegerField()
    fare = models.IntegerField()
    date = models.DateField()
    time = models.TimeField()

    def _str_(self):
        return self.bus_name
    

class Booking(models.Model):
    BOOKED = 'B'
    CANCELLED = 'C'

    TICKET_STATUS = ((BOOKED, 'Booked'),
                       (CANCELLED, 'Cancelled'),)
    user=models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    bus=models.ForeignKey(Bus,on_delete=models.CASCADE)
    no_seat_booked = models.IntegerField()
    payment_amount=models.DecimalField(max_digits=10,decimal_places=2,null=True)
    refund_amount=models.DecimalField(max_digits=10,decimal_places=2,null=True)
    status = models.CharField(choices=TICKET_STATUS, default=BOOKED, max_length=20)
    

class PaymentRecords(models.Model):
    id = models.AutoField(primary_key=True) 
    user=models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(auto_now_add=True)
    amount_refunded = models.DecimalField(max_digits=10, decimal_places=2,null=True)
    refunded_at = models.DateTimeField(null=True)
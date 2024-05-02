from rest_framework import serializers
from .models import CustomUser,PaymentRecords

class RegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id','username','fullname','gender','age','email']

class PaymentRecordsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentRecords
        fields = '__all__'
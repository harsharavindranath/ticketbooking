# Generated by Django 5.0.4 on 2024-04-30 13:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bookingapp', '0003_alter_paymentrecords_id_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='paymentrecords',
            name='id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
    ]
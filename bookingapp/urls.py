from django.urls import path
from  .views import *

urlpatterns=[
    path('Registration/',Registration),
    path('user_login/',user_login),
    path('user_logout/',user_logout),
    path('userhomepage/',userhomepage),
    path('findbus/',findbus),
    path('book_bus/',book_bus),
    path('make_payment/',make_payment),
    path('cancel_booking/',cancel_booking),
    path('refund_amount/',refund_amount)
]
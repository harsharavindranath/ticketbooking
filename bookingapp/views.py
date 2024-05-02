from rest_framework.response import Response
from .models import *
from rest_framework.decorators import api_view,permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .serializers import RegistrationSerializer,PaymentRecordsSerializer
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken,AccessToken

from datetime import datetime,timedelta
from django.utils import timezone


# Create your views here.
@api_view(['POST'])
def Registration(request):
    if request.method == 'POST':
        # Extracting data from request
        username = request.data.get('username')
        fullname = request.data.get('fullname')
        age = request.data.get('age')
        gender = request.data.get('gender')
        email = request.data.get('email')
        password = request.data.get('password')
        # Check if the username already exists
        if CustomUser.objects.filter(username=username).exists():
            return Response({"message": "User with this username already exists"}, status=status.HTTP_400_BAD_REQUEST)
        # Check if the email already exists
        if CustomUser.objects.filter(email=email).exists():
            return Response({"message": "User with this email already exists"}, status=status.HTTP_400_BAD_REQUEST)
        # Create the user
        user = CustomUser.objects.create_user(username=username, fullname=fullname, age=age, gender=gender, email=email, password=password)
        # Serialize the user data
        serializer = RegistrationSerializer(user)
        # Return response with registered user data
        return Response({'message': 'User registered successfully','user': serializer.data}, status=status.HTTP_201_CREATED)
    # If request method is not POST
    return Response({'error': 'Method not allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)



@api_view(['POST'])
def user_login(request):
    username = request.data.get('username')
    password = request.data.get('password')
    # Authenticate user
    user = authenticate(username=username, password=password)
    if user:
        # Generate refresh token
        refresh = RefreshToken.for_user(user)
        # Generate access token
        access_token = AccessToken.for_user(user)
        # Return refresh and access tokens along with user information
        return Response({
            'refresh': str(refresh),
            'access': str(access_token),
            'user':{'id': user.id,'username': user.username,'email':user.email},}, status=status.HTTP_200_OK)
    else:
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def user_logout(request):
    refresh_token = request.data.get('refresh')
    if refresh_token:
        # Blacklist the refresh token
        refresh_token = RefreshToken(refresh_token)
        refresh_token.blacklist()
        return Response({'message': 'Logout successful'}, status=status.HTTP_200_OK)
    else:
        return Response({'error': 'Refresh token not provided'}, status=status.HTTP_400_BAD_REQUEST)
    

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def userhomepage(request):
    if not request.user.is_authenticated:
        return Response({"error": "Authentication Required"}, status=status.HTTP_401_UNAUTHORIZED)
    payment_records = PaymentRecords.objects.filter(user=request.user)
    serializer = PaymentRecordsSerializer(payment_records, many=True)
    return Response(serializer.data)


    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def findbus(request):
    if not request.user.is_authenticated:
        return Response({"error": "Authentication Required"}, status=status.HTTP_401_UNAUTHORIZED)
    if request.method == 'GET':
        source = request.data.get('source')
        destination = request.data.get('destination')
        bus_list = Bus.objects.filter(source=source, destination=destination)
        if bus_list.exists():
            buses_data = []
            for bus in bus_list:
                bus_data = {
                    'bus_type':bus.type,
                    'bus_name': bus.bus_name,
                    'source': bus.source,
                    'destination': bus.destination,
                    'no_of_seat': bus.no_of_seat,
                    'rem_seat': bus.rem_seat,
                    'fare': bus.fare,
                    'date': bus.date.strftime('%Y-%m-%d'),
                    'time': bus.time.strftime('%H:%M:%S')
                }
                buses_data.append(bus_data)
            return Response({'buses': buses_data})
        else:
            return Response({"error": "Sorry, no buses available for the given criteria"}, status=status.HTTP_404_NOT_FOUND)
    else:
        return Response({"error": "Method not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def book_bus(request):
    if not request.user.is_authenticated:
        return Response({"error": "Authentication Required"}, status=status.HTTP_401_UNAUTHORIZED)
    if request.method == 'POST':
        user = request.user
        bus_name = request.data.get('bus_name')
        no_of_seat = int(request.data.get('no_of_seat', 0))
        if Bus.objects.filter(bus_name=bus_name).exists():
            bus=Bus.objects.get(bus_name=bus_name)
        else:
            return Response({"error": "Bus not found"}, status=status.HTTP_404_NOT_FOUND)
        if no_of_seat <= 0:
            return Response({"error": "Invalid number of seats"}, status=status.HTTP_400_BAD_REQUEST)
        if bus.rem_seat < no_of_seat:
            return Response({"error": "Not enough available seats"}, status=status.HTTP_400_BAD_REQUEST)
        payment_amount = bus.fare * no_of_seat  # fare is per seat
        # Create booking 
        booking = Booking.objects.create(
            user=user,
            bus=bus,
            no_seat_booked=no_of_seat,
            payment_amount=payment_amount,
            status=Booking.BOOKED
        )
        # Update remaining seats
        bus.rem_seat -= no_of_seat
        bus.save()
        # Retrieve booked data of the logged-in user
        user_bookings = Booking.objects.filter(user=user)
        booked_data = []
        for booking in user_bookings:
            booked_data.append({
                'booking_id': booking.id,
                'user': booking.user.fullname,
                'bus_name': booking.bus.bus_name,
                'source': booking.bus.source,
                'destination': booking.bus.destination,
                'no_of_seat': booking.no_seat_booked,
                'payment_amount': booking.payment_amount,
                'date_of_journey': booking.bus.date.strftime('%Y-%m-%d'),
                'Bus_time': booking.bus.time.strftime('%H:%M:%S'),
                'status': booking.status
            })
        return Response({"message": "Booking successful", "booking_id": booking.id, "bookings": booked_data}, status=status.HTTP_201_CREATED)
    else:
        return Response({"error": "Method not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def make_payment(request):
    if not request.user.is_authenticated:
        return Response({"error": "Authentication Required"}, status=status.HTTP_401_UNAUTHORIZED)
    if request.method == 'POST':
        user = request.user
        booking_id = request.data.get('booking_id')
        amount_paid = float(request.data.get('amount_paid', 0))
        if Booking.objects.filter(id=booking_id,user=user, status=Booking.BOOKED).exists():
            booking=Booking.objects.get(id=booking_id)
        else:
            return Response({"error": "Booking not found"}, status=status.HTTP_404_NOT_FOUND)
        if amount_paid <= 0:
            return Response({"error": "Invalid amount paid"}, status=status.HTTP_400_BAD_REQUEST)
        if amount_paid < booking.payment_amount:
            return Response({"message": "Insufficient amount paid"}, status=status.HTTP_400_BAD_REQUEST)
        # Create payment record
        payment_record = PaymentRecords.objects.create(user=user,booking=booking,amount_paid=amount_paid)
        return Response({"message": "Payment successful", "payment_id": payment_record.id}, status=status.HTTP_201_CREATED)
    else:
        return Response({"error": "Method not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cancel_booking(request):
    if request.method == 'POST':
        user = request.user
        booking_id = request.data.get('booking_id')
        if not booking_id:
            return Response({"error": "Booking ID is required"}, status=status.HTTP_400_BAD_REQUEST)
        if Booking.objects.filter(id=booking_id, user=user, status=Booking.BOOKED).exists():
            booking=Booking.objects.get(id=booking_id, user=user, status=Booking.BOOKED)
        else:
            return Response({"error": "Booking not found or already cancelled"}, status=status.HTTP_404_NOT_FOUND)
        # Calculate time difference between current time and departure time of the bus
        departure_time = datetime.combine(booking.bus.date, booking.bus.time)
        current_time = datetime.now()
        time_difference = departure_time - current_time
        # Calculate refund amount based on the time difference
        if time_difference >= timedelta(days=1):  # 24 hours or more before departure
            refund_amount = booking.payment_amount
        else:
            refund_amount = booking.payment_amount / 2  # Half refund if less than 24 hours before departure
        # Free up the seats
        bus = booking.bus
        bus.rem_seat += booking.no_seat_booked
        bus.save()
        # Cancel the booking and save refund amount
        booking.status = Booking.CANCELLED
        booking.refund_amount = refund_amount
        booking.save()
        return Response({"message": "Booking cancelled successfully", "refund_amount": refund_amount}, status=status.HTTP_200_OK)
    else:
        return Response({"error": "Method not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def refund_amount(request):
    if request.method == 'POST':
        user = request.user
        booking_id = request.data.get('booking_id')
        payment_id = request.data.get('payment_id')
        booking = Booking.objects.get(id=booking_id, user=user, status=Booking.CANCELLED)
        if not booking:
            return Response({"error": "Cancelled booking not found"}, status=status.HTTP_404_NOT_FOUND)
        if booking.refund_amount is None:
            return Response({"error": "Refund amount not available"}, status=status.HTTP_400_BAD_REQUEST) 
        # Update the existing payment record to mark it as refunded
        refunded_record=PaymentRecords.objects.get(id=payment_id)
        refunded_record.amount_refunded = booking.refund_amount
        refunded_record.refunded_at=timezone.now()
        refunded_record.save() 
        return Response({"message": "Refund successful", "payment_id": refunded_record.id}, status=status.HTTP_201_CREATED)
    else:
        return Response({"error": "Method not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
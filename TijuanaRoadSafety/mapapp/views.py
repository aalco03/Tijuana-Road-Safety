import os
import tempfile
import requests
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
from django.core.files.base import ContentFile
from django.conf import settings
from django.db.models import F
# Twilio imports temporarily disabled for deployment
# try:
#     from twilio.twiml.messaging_response import MessagingResponse
#     TWILIO_AVAILABLE = True
# except ImportError:
#     TWILIO_AVAILABLE = False
#     MessagingResponse = None
TWILIO_AVAILABLE = False

# Roboflow AI detection using HTTP API (no OpenCV required)
def detect_pothole_via_api(image_path, api_key):
    """
    Use Roboflow's HTTP API to detect potholes without requiring OpenCV
    """
    if not api_key:
        return {'predictions': []}
    
    try:
        # Read image file
        with open(image_path, 'rb') as image_file:
            # Roboflow API endpoint
            api_url = "https://detect.roboflow.com/pothole-detection-bqu6s/9"
            
            # Make API request
            response = requests.post(
                f"{api_url}?api_key={api_key}",
                files={"file": image_file}
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Roboflow API error: {response.status_code}")
                return {'predictions': []}
                
    except Exception as e:
        print(f"Roboflow API exception: {e}")
        return {'predictions': []}

AI_AVAILABLE = bool(settings.ROBOFLOW_API_KEY)

from .forms import PotholeReportForm
from .models import PotholeReport
from .forms import AuditReportForm
from PIL import Image


def home(request):
    reports = PotholeReport.objects.all()
    # Get top potholes ranked by submission count, then by latest submission date
    top_potholes = PotholeReport.objects.all().order_by('-submission_count', '-latest_submission_date')[:10]
    
    # Debug: Print image URLs to console
    for pothole in top_potholes:
        if pothole.image:
            print(f"Pothole #{pothole.id} image URL: {pothole.image.url}")
            print(f"Pothole #{pothole.id} image path: {pothole.image.path}")
    
    return render(request, 'home.html', {
        'reports': reports, 
        'top_potholes': top_potholes,
        'google_maps_api_key': settings.GOOGLE_MAPS_API_KEY
    })

def report_pothole(request):
    if request.method == 'POST':
        form = PotholeReportForm(request.POST, request.FILES)
        if form.is_valid():
            image_file = form.cleaned_data['image']

            with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file: #WILL ALTER WHEN ESTABLISH DB
                image = Image.open(image_file)
                # Convert RGBA to RGB before saving as JPEG
                if image.mode == 'RGBA':
                    # Create a white background image
                    background = Image.new('RGB', image.size, (255, 255, 255))
                    # Paste the image on the background
                    background.paste(image, mask=image.split()[3])  # 3 is the alpha channel
                    # Save the new image
                    background.save(temp_file, format='JPEG')
                else:
                    # If it's already RGB, just save it
                    image.save(temp_file, format='JPEG')
                temp_file_path = temp_file.name

            #ROBOFLOW MODEL IMAGE INFERENCE
            try:
                if AI_AVAILABLE:
                    result = detect_pothole_via_api(temp_file_path, settings.ROBOFLOW_API_KEY)
                else:
                    result = {'predictions': []}
                
                if result['predictions']:
                    prediction = result['predictions'][0] 
                    if prediction['confidence'] >= 0.8 and prediction['class'] == "Pothole": #ALTER IF WE WANT TO MAKE THRESHOLD LOWER
                        # Save with AI confidence score
                        report = form.save(commit=False)
                        report.ai_confidence_score = prediction['confidence']
                        report.save()
                        return redirect('thank_you')
                    else:
                        form.add_error(None, "The submitted image does not appear to contain a pothole. Please try to take a clearer picture.")
                else:
                    # If AI detection fails or no API key, still allow manual submission
                    if not AI_AVAILABLE:
                        form.save()
                        return redirect('thank_you')
                    else:
                        form.add_error(None, "The submitted image does not appear to contain a pothole. Please try to take a clearer picture.")
                    
            finally:
                os.remove(temp_file_path)

        return render(request, 'report_pothole.html', {'form': form}) 
    else:
        form = PotholeReportForm()
    return render(request, 'report_pothole.html', {'form': form, 'google_maps_api_key': settings.GOOGLE_MAPS_API_KEY}) 

def report_detail(request, report_id):
    report = get_object_or_404(PotholeReport, pk=report_id)
    return render(request, 'report_detail.html', {
        'report': report,
        'google_maps_api_key': settings.GOOGLE_MAPS_API_KEY
    })

#SECTION FOR AUDITING REPORT
def audit_report(request, report_id):
    report = get_object_or_404(PotholeReport, pk=report_id)

    if request.method == 'POST':
        form = AuditReportForm(request.POST, request.FILES)
        if form.is_valid():
            audit_phone_number = request.POST.get('phone_number', '')
            if audit_phone_number and audit_phone_number == report.phone_number:
                report.delete()
                return redirect('home')
            else:
                return render(request, 'audit_processing.html')
    else:
        form = AuditReportForm()

    return render(request, 'audit_report.html', {'form': form, 'report': report})

def thank_you(request):
    return render(request, 'thank_you.html')

#WHATSAPP REPORT RECEPTION
@csrf_exempt
def whatsapp_webhook(request):
    if not TWILIO_AVAILABLE:
        return HttpResponse("Twilio not available", status=503)
    
    if request.method == 'POST':
        incoming_msg = request.POST.get('Body', '').lower()
        from_number = request.POST.get('From').replace('whatsapp:', '')  
        media_url = request.POST.get('MediaUrl0', None)
        lat = request.POST.get('Latitude', None)
        lon = request.POST.get('Longitude', None)

        twilio_sid = settings.TWILIO_ACCOUNT_SID
        twilio_auth_token = settings.TWILIO_AUTH_TOKEN

        session = request.session
        if 'submission' not in session:
            session['submission'] = {}

        resp = MessagingResponse()
        msg = resp.message()

        #CHECK SESSION DATA TO ENSURE DEPLOYMENT OF WELCOME MESSAGE IF FIRST MESSAGE IN SESSION
        if 'first_message_sent' not in session:
            # Send the initial welcome message automatically
            msg.body("Welcome to Road Safety Tijuana! Please send 'new report' if you would like to make a report.")
            session['first_message_sent'] = True  #AVOID RESENDING WELCOME MESSAGE
            session.modified = True  
            return HttpResponse(str(resp))  

        # If user types "new report", reset the flow and ask for inputs
        if 'new report' in incoming_msg:
            msg.body("Please provide, in three separate messages, an image of the pothole, a pin with its location, and a rating from 1 through 5 on the severity of the pothole.")
            session['submission'] = {}  # Reset submission data
            session.modified = True
            return HttpResponse(str(resp))

        # Handle image submission
        elif media_url:
            try:
                response = requests.get(media_url, auth=(twilio_sid, twilio_auth_token))
                response.raise_for_status()

                # Use Roboflow to check if the image contains a pothole
                with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
                    temp_file.write(response.content)
                    temp_file_path = temp_file.name

                if AI_AVAILABLE:
                    result = detect_pothole_via_api(temp_file_path, settings.ROBOFLOW_API_KEY)
                else:
                    result = {'predictions': []}

                if result['predictions']:
                    prediction = result['predictions'][0]
                    if prediction['confidence'] >= 0.8 and prediction['class'] == "Pothole":
                        # Store the image URL and AI confidence in the session
                        session['submission']['image_url'] = media_url
                        session['submission']['ai_confidence'] = prediction['confidence']
                        session.modified = True
                        msg.body("Image received! Now, please send the location of the pothole as a pin.")
                    else:
                        msg.body("The image does not appear to be a pothole. Please send a clearer image.")
                else:
                    msg.body("The image does not appear to be a pothole. Please send a clearer image.")

                os.remove(temp_file_path)  # Clean up temp file

            except requests.RequestException as e:
                msg.body(f"Failed to download the image. Error: {str(e)}")

        # Handle location submission (pin)
        elif lat and lon:
            session['submission']['latitude'] = lat
            session['submission']['longitude'] = lon
            session.modified = True
            msg.body("Location received! Now, please send a rating from 1 to 5 on the severity of the pothole.")

        # Handle severity rating
        elif incoming_msg.isdigit() and 1 <= int(incoming_msg) <= 5:
            session['submission']['severity'] = incoming_msg
            session.modified = True

            # Now, check if we have all the required data (image, location, severity)
            if 'image_url' in session['submission'] and 'latitude' in session['submission'] and 'longitude' in session['submission']:
                media_url = session['submission'].pop('image_url')

                try:
                    response = requests.get(media_url, auth=(twilio_sid, twilio_auth_token))
                    response.raise_for_status()

                    form_data = {
                        'phone_number': from_number,
                        'severity': session['submission']['severity'],
                        'latitude': session['submission']['latitude'],
                        'longitude': session['submission']['longitude'],
                        'submission_source': 'whatsapp',
                        'whatsapp_message_id': request.POST.get('MessageSid', ''),
                        'ai_confidence_score': session['submission'].get('ai_confidence', None),
                        'status': 'verified',  # WhatsApp submissions are pre-verified by AI
                    }
                    form = PotholeReportForm(form_data, {'image': ContentFile(response.content, name="pothole_image.jpg")})
                    if form.is_valid():
                        form.save()
                        msg.body("Thank you for your submission! The map has been updated. If you'd like to make another report, type 'new report'.")
                        session['submission'] = {}  # Clear session after successful submission
                    else:
                        print("Form errors:", form.errors)
                        msg.body("There was an error with your submission. Please try again.")
                except requests.RequestException as e:
                    msg.body(f"Failed to download the image. Error: {str(e)}")
            else:
                msg.body("Submission incomplete. Please provide all the required information.")

        else:
            # Catch-all for incomplete information or invalid inputs
            if 'image_url' not in session['submission']:
                msg.body("Please share an image of the pothole.")
            elif 'latitude' not in session['submission'] or 'longitude' not in session['submission']:
                msg.body("Please share the location (pin) of the pothole.")
            elif 'severity' not in session['submission']:
                msg.body("Please provide a severity rating from 1 to 5 for the pothole.")

        return HttpResponse(str(resp))
    return HttpResponse('OK', status=200)

@csrf_exempt
def submit_pothole_report(session, from_number, msg):
    # Create form data for submission
    form_data = {
        'phone_number': from_number,
        'severity': '3',  # Default severity for now
        'latitude': session['submission']['latitude'],
        'longitude': session['submission']['longitude']
    }

    # If the image is a URL (from WhatsApp), we need to download it and convert it to a file-like object
    image_url = session['submission']['image']
    try:
        # Twilio requires basic authentication to access media, so we pass the account SID and auth token
        twilio_sid = settings.TWILIO_ACCOUNT_SID
        twilio_auth_token = settings.TWILIO_AUTH_TOKEN

        response = requests.get(image_url, auth=(twilio_sid, twilio_auth_token))
        response.raise_for_status()  # Check for request errors

        # Create a file-like object from the downloaded image
        image_content = ContentFile(response.content)
        image_content.name = "pothole_image.jpg"  # Make sure the file has a name

        # Create and validate the form
        form = PotholeReportForm(form_data, {'image': image_content})

        if form.is_valid():
            form.save()
            msg.body("Thank you for your submission! The map has been updated.")
            session['submission'] = {}  # Clear session data after submission
        else:
            print("Form Errors: ", form.errors)
            msg.body("There was an error with your submission. Please try again.")

    except requests.RequestException as e:
        msg.body(f"Failed to download the image. Please try again later. Error: {str(e)}")

# API endpoint for checking nearby potholes
def check_nearby_potholes(request):
    if request.method == 'POST':
        try:
            latitude = float(request.POST.get('latitude'))
            longitude = float(request.POST.get('longitude'))
            
            nearby_potholes = PotholeReport.find_nearby_potholes(latitude, longitude, radius_meters=50)
            
            pothole_data = []
            for item in nearby_potholes:
                pothole = item['pothole']
                pothole_data.append({
                    'id': pothole.id,
                    'latitude': pothole.latitude,
                    'longitude': pothole.longitude,
                    'severity': pothole.severity,
                    'submission_count': pothole.submission_count,
                    'distance': round(item['distance'], 2),
                    'image_url': pothole.image.url if pothole.image else None,
                    'approximate_address': pothole.approximate_address or 'Address not available'
                })
            
            return JsonResponse({'nearby_potholes': pothole_data})
        except (ValueError, TypeError):
            return JsonResponse({'error': 'Invalid coordinates'}, status=400)
    
    return JsonResponse({'error': 'POST request required'}, status=405)

# API endpoint for incrementing pothole submission count
def increment_pothole_count(request):
    if request.method == 'POST':
        try:
            pothole_id = int(request.POST.get('pothole_id'))
            pothole = get_object_or_404(PotholeReport, id=pothole_id)
            pothole.increment_submission_count()
            
            return JsonResponse({
                'success': True,
                'new_count': pothole.submission_count,
                'message': 'Thank you for confirming this existing pothole report!'
            })
        except (ValueError, TypeError):
            return JsonResponse({'error': 'Invalid pothole ID'}, status=400)
    
    return JsonResponse({'error': 'POST request required'}, status=405)
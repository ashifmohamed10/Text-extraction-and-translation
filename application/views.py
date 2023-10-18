from django.shortcuts import render,redirect

from application.models import ImageUpload,ExtractedData,TextUpload,PdfUpload,AudioUpload
from django.http import JsonResponse
from pytesseract import pytesseract
from PIL import Image
from django.http import HttpResponse

import pdfplumber
from googletrans import LANGUAGES
from .translator import translate_text
import speech_recognition as sr

from transformers import GPT2LMHeadModel, GPT2Tokenizer
import pyttsx3

import tempfile
from pydub import AudioSegment

import os

def base(request):
    return render(request,'home.html')

def image_upload(request):
    if(request.method=="POST"):
        i=request.FILES.get('i')
        img=ImageUpload.objects.create(files=i)
        img.save()
        return imageextract(request)

    return render(request,'imageupload.html')

model_name = "gpt2"
model = GPT2LMHeadModel.from_pretrained(model_name)
tokenizer = GPT2Tokenizer.from_pretrained(model_name)

def generate_predictive_text(input_text):
    input_ids = tokenizer.encode(input_text, return_tensors="pt")
    output = model.generate(input_ids, max_length=50, num_return_sequences=1, temperature=0.7)
    predicted_text = tokenizer.decode(output[0], skip_special_tokens=True)
    return predicted_text

def text_upload(request):
    if request.method == "POST":
        user_input = request.POST.get('t')
        data = TextUpload.objects.create(text=user_input)
        data.save()
        predictive_text = generate_predictive_text(user_input)
        return render(request, 'textupload.html', {'user_input':user_input,'predictive_text': predictive_text})

    return render(request, 'textupload.html')



def pdf_upload(request):
    if request.method == "POST":
        p = request.FILES.get('p')
        pdf = PdfUpload.objects.create(files=p)
        pdf.save()
        return pdf_extract(request)

    return render(request, 'pdfupload.html')


def imageextract(request):
    if request.method == 'POST':
        # Get the uploaded image
        img = ImageUpload.objects.latest('uploaded_at') # You might want to filter or select the image in a specific way

        if img:
            image = Image.open(img.files.path)
            pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

            # Perform OCR to extract text from the image
            extracted_text = pytesseract.image_to_string(image)

            # Create a new ExtractedData object and save the extracted text
            data = ExtractedData.objects.create(text=extracted_text)
            data.save()

            # Return the extracted text as JSON
            return render(request, 'extracted.html', {'extracted_text': extracted_text})
        else:
            return render(request, 'errorpage.html', {'error': 'No image uploaded'})

    return render(request, 'imgextract.html')

def pdf_extract(request):
    if request.method == "POST":
        try:
            pdf = PdfUpload.objects.latest("uploaded_at")
            if pdf and pdf.files:
                # Check if the 'files' attribute is not None
                with pdfplumber.open(pdf.files.path) as pdf_doc:
                    extracted_text = ""
                    for page in pdf_doc.pages:
                        extracted_text += page.extract_text()
                        data = ExtractedData.objects.create(text=extracted_text)
                        data.save()


                # You can now use 'extracted_text' in your template or perform further processing
                return render(request, 'extracted.html', {'extracted_text': extracted_text})
            else:
                # Handle the case where 'pdf' or 'pdf.files' is None
                return render(request, 'errorpage.html', {'error_message': 'No PDF file found.'})
        except PdfUpload.DoesNotExist:
            # Handle the case where no PdfUpload objects are found
            return render(request, 'errorpage.html', {'error_message': 'No PDF uploaded yet.'})

    return render(request, 'pdfextract.html')

def getdata(request):
    data=ExtractedData.objects.latest('uploaded_at')
    data_str=data.text
    print(data_str)
    print(type(data_str))
    return render(request, 'home.html')

def translation(request):
    if request.method == "POST":
        lang_code = request.POST.get('lang_code')

        data = ExtractedData.objects.latest('uploaded_at')
        data_str = data.text

        translated_text = translate_text(data_str, "en", lang_code)
        return render(request, 'translated.html', {'translated_text': translated_text})
    return render(request, 'translate.html')

# def text_extract(request):
#     if request.method=="POST":
#         data=TextUpload.objects.latest('uploaded_at')
#         if data:
#             obj=ExtractedData()
#             obj.text=data.text
#             obj.save()
#         else:
#             pass
#         return translation(request)

def get_text(request):
    text=TextUpload.objects.latest('uploaded_at')
    return render(request,'text.html',{'text':text})

def text_translation(request):
    if request.method == "POST":
        lang_code = request.POST.get('lang_code')
        pre_data = TextUpload.objects.latest('uploaded_at')
        data_str = pre_data.text

        translated_text = translate_text(data_str, "en", lang_code)
        return render(request, 'translated.html', {'translated_text': translated_text})
    return render(request, 'translate.html')



def audio_extract(request):
    listener = sr.Recognizer()
    try:
        with sr.Microphone() as source:

            voice=listener.listen(source)
            extracted_text=listener.recognize_google(voice)
            data=ExtractedData.objects.create(text=extracted_text)
            data.save()
            return render(request,'extracted.html',{'extracted_text':extracted_text})
    except:
        pass
    return render(request,'extracted.html')




























































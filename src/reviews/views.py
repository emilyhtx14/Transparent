from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
import math
from django.http.response import HttpResponse
from django.http import HttpResponseRedirect
from .forms import UploadFileForm
import urllib.request
import os, io
import json
import requests
from googleapiclient.discovery import build
from .gcloud import GoogleCloudMediaFileStorage
# import regular expressions to clean things up
import re
from bs4 import BeautifulSoup
from google.cloud import vision_v1
from google.cloud.vision_v1 import types
from google.cloud import language_v1
from .models import Matching, Comment
import argparse
from .forms import MatchingForm, CommentForm
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = "/Users/emilyhuang/Downloads/service-account-file.json"
client = vision_v1.ImageAnnotatorClient()


    #return render(request, "reviews/maps_view.html", {})

def post(self, request):
    image = request.FILES['image']
    public_uri = Upload.upload_image(image, image.name)
    return HttpResponse("<img src='%s'/>" % public_uri)

def maps_test_view(request):
    return render(request, "reviews/maps_test.html", {})
"""
def maps_view(request):
    api_key = 'AIzaSyChj4_T1N200RhQMuyv-kmQDuKKa7PwuIg'
    origin = input("Enter a home address") #'2500+E+Kearney+Springfield+MO+65898'
    destination = input("Enter a work address") #'405+N+Jefferson+Ave+Springfield+MO+65806'
    url = ('https://maps.googleapis.com/maps/api/distancematrix/json'
           + '?language=en-US&units=imperial'
           + '&origins={}'
           + '&destinations={}'
           + '&key={}'
           ).format(origin, destination, api_key)
    response = urllib.request.urlopen(url)
    r = json.loads(response.read())
    time = r['rows'][0]['elements'][0]['duration']['text']
    miles = r['rows'][0]['elements'][0]['distance']['text']
    print("\n The total travel time from home to work by car is", time)
    print("\n The total distance is", miles)

    return render(request, "reviews/maps_view.html", {})

"""


def maps_view(request):
    form = MatchingForm(request.POST or None)
    if form.is_valid():
        form.save()
        form = MatchingForm()
        return redirect('/results')
    context = {
        'form': form
    }
    return render(request, "reviews/review_create.html", context)

def maps_detail_view(request):

    user_list = Matching.objects.all()
    user_name = user_list.latest('id').name
    user_sell = user_list.latest('id').sell_topics
    user_buy = user_list.latest('id').buy_topics
    user_city = user_list.latest('id').city
    user_study = user_list.latest('id').study_topics
    user_email = user_list.latest('id').email

    points = 0.0
    points_dict = {}
    distance_dict = {}
    shipping_dict = {}
    for student in user_list:
        student_name = student.name
        if(student == user_name):
            break
        if(student_name in points_dict):
            pass
        else:
            points_dict[student_name] = 0

        student_sell = student.sell_topics.split(',')
        student_buy = student.buy_topics.split(',')
        student_city = student.city
        student_study = student.study_topics.split(',')
        student_email = student.email

        # seller/buyer  + study/buddy match
        for topic in student_sell:
            if topic in user_buy:
                points_dict[student_name] += 60

        for topic in student_buy:
            if topic in user_sell:
                points_dict[student_name] += 60

        for topic in student_study:
            if topic in user_study:
                points_dict[student_name] += 60


        # location map stuff
        api_key = 'AIzaSyChj4_T1N200RhQMuyv-kmQDuKKa7PwuIg'
        origin = user_city  # '2500+E+Kearney+Springfield+MO+65898'
        destination = student_city  # '405+N+Jefferson+Ave+Springfield+MO+65806'
        url = ('https://maps.googleapis.com/maps/api/distancematrix/json'
               + '?language=en-US&units=imperial'
               + '&origins={}'
               + '&destinations={}'
               + '&key={}'
               ).format(origin, destination, api_key)
        response = urllib.request.urlopen(url)
        r = json.loads(response.read())
        # time in hours
        # time = r['rows'][0]['elements'][0]['duration']['value']/3600
        # distance in miles


        miles = r['rows'][0]['elements'][0]['distance']['value']/1600
        # shipping cost calculation for one textbook via ups: price = 0.00153miles + 11.5
        shipping_cost = 0.00153 * miles + 11.5
        shipping_cost = "{:.2f}".format(shipping_cost)
        # shipping_cost = float(shipping_cost)
        shipping_dict[student_name] = shipping_cost
        distance_dict[student_name] = r['rows'][0]['elements'][0]['distance']['text']

        if(miles <= 20):
            points_dict[student_name] += 20
        elif(miles <= 100):
            points_dict[student_name] += 10
        elif (miles <= 200):
            points_dict[student_name] += 10
        elif (miles <= 400):
            points_dict[student_name] += 10
        elif (miles <= 800):
            points_dict[student_name] -= 10
        elif (miles <= 1100):
            points_dict[student_name] -= 20
        elif (miles <= 1400):
            points_dict[student_name] -= 30
        elif(miles <= 1700):
            points_dict[student_name] -= 40
        elif (miles > 1700):
            points_dict[student_name] -= 50

    context = {
        'points': points_dict,
        'user_list': user_list,
        'last_user': user_name,
        'distances': distance_dict,
        'shipping':shipping_dict
    }
    return render(request, "reviews/maps_detail.html", context)

def language_analysis(text):
    client = language_v1.LanguageServiceClient()
    document = language_v1.Document(content = text, type_=language_v1.Document.Type.PLAIN_TEXT)
    # document = client.document_from_text(text)
    sent_analysis = client.analyze_sentiment(request={'document':document}).document_sentiment
    sentiment = sent_analysis
    return sentiment

def comment_create(request):
    """
    if request.is_ajax():
        data = json.loads(request.POST.get('coord'))
        print(data)
     """
    keywords = request.session['format_text']   
    form = CommentForm(request.POST or None)
    if form.is_valid():
        form.save()
        form = CommentForm()
        return redirect('/reviews')
    context = {
        'form': form,
        'keywords':keywords
    }
    return render(request, "reviews/comment_create.html", context)
    

def review_view(request):
    # covered topics: mathematics, physics, computer science,
    key_terms = ['algebra', 'topology', 'geometry', 'multivariable', 'calculus', 'analysis', 'trigonometry',
                 'number theory', 'arithmetic', 'probability', 'statistic', 'combinatorics',
                 'discrete mathematics', 'linear algebra', 'algebraic geometry', 'set theory', 'fraction',
                 'differential', 'electromagnetism', 'quantum', 'mechanics',
                 'nuclear', 'physics', 'thermodynamics', 'astrophysics', 'biophysics', 'optics', 'relativity',
                 'particle physics', 'cosmology', 'solid-state', 'atomic', 'molecular',
                 'acoustics', 'astronomy', 'gravity', 'geophysics', 'python', 'java', 'javascript', 'react', 'css',
                 'html', 'scala','coding','biology','organizational','economics','business', 'entrepreneur', 'management',
                 'supply','accounting','law','number theory','optimization','trigonometry', 'MATLAB']

    sites = []
    format_text = []
    videos = []
    comments = []
    keyword = ""
    sent_score = {}
    sent_mag = {}
    art_comments = {}
    actual_name = ""
    art_sent = 0
    art_mag = 0
    

    if request.method == 'POST':
        path = request.FILES['myfile']
        """
        with io.open(path, 'rb') as image_file:
            content = image_file.read()
        """
        content = path.read()
        image = vision_v1.types.Image(content=content)

        response1 = client.text_detection(image=image)
        texts = response1.text_annotations
        print('Texts:')
        for text in texts:
            # format_text.append('"{}"'.format(text.description))
            format_text.append(text.description)
        
                ## newly added stuff
        request.session['format_text'] = format_text

        for word in format_text:
            word.replace('"',"")
            if str(word).lower() in key_terms:
                keyword = str(word).lower()
                break
        print(keyword)
        ### yt search begin
        
        search_url = 'https://www.googleapis.com/youtube/v3/search'
        video_url = 'https://www.googleapis.com/youtube/v3/videos'
        comment_url = 'https://www.googleapis.com/youtube/v3/commentThreads'

        format_text.pop(0)

        for i in range(0,3):
            actual_name += str(format_text[i]) 
            if i != 2:
               actual_name += " "
        print("actual name:", actual_name)
        print("format_text", format_text)

        search_params = {
            'part': 'snippet',
            'q': actual_name,# 'multivariable calculus',
            'key': 'AIzaSyDzHsY1o1ySzENf7O4dm7wR47wD-fhk5PQ',
            'maxResults': 4,
            'type': 'video'
        }

        video_ids = []
        r = requests.get(search_url, params=search_params)
        results = r.json()['items']
        for result in results:
            video_ids.append(result['id']['videoId'])

        video_params = {
            'part': 'snippet,contentDetails',
            'key': 'AIzaSyDzHsY1o1ySzENf7O4dm7wR47wD-fhk5PQ',
            'id': ','.join(video_ids),
            'max_results': 4
        }

        r = requests.get(video_url, params=video_params)
        results = r.json()['items']
        videos = []
        for result in results:
            # print(result['contentDetails']['duration'])
            video_data = {
                'title': result['snippet']['title'],
                'id': result['id'],
                'url': f'https://www.youtube.com/watch?v={result["id"]}',
                'thumbnails': result['snippet']['thumbnails']['high']['url']
            }
            videos.append(video_data)

        comments = []
        comment_dict = {}
        for id_num in video_ids:
            comment_params = {
                'part': 'snippet',
                'key': 'AIzaSyDzHsY1o1ySzENf7O4dm7wR47wD-fhk5PQ',
                'videoId': id_num,
                'max_results': 5
            }

            r2 = requests.get(comment_url, params=comment_params)
            # print(r2.text)
            results2 = r2.json()['items']

            #{video_id: string of comments for that id}

            for result in results2:
                print("results: ", result)
                cmt = result['snippet']['topLevelComment']['snippet']['textDisplay']
                com_vid_id = result['snippet']['videoId']
                comment_data = {
                    #'id': id_num,
                    'id': com_vid_id,
                    'comment_text': cmt
                }

                comments.append(comment_data)
                if id_num == com_vid_id:
                    if id_num in comment_dict:
                        comment_dict[id_num] = comment_dict[id_num] + cmt
                    else:
                        comment_dict[id_num] = cmt

        # comment_dict maps the video id to a string that consists of all the comments in that video
        # print("comment dictionary: ", comment_dict)

        for key, value in comment_dict.items():
            # print("video id- ", key)
            # print("current comment thread ", value )
            my_text = language_analysis(value)
            sent_score[key] = my_text.score
            sent_mag[key] = my_text.magnitude
            # sent_mag[vid_id] = language_analysis(value).document_sentiment.magnitude
            # print("This is the current sentiment score: ", sent_score)

        ### yt search end #
       
        ### start of vision api web detection, uncomment when ready

        response = client.web_detection(image=image)
        web_detection = response.web_detection

        # ['pages_with_matching_images','partial_matching_images']

        my_formatted_text = web_detection.pages_with_matching_images
        print('\n{} Pages with matching images retrieved'.format(
                len(my_formatted_text)))

        for page in my_formatted_text:
            sites.append(format(page.url))
        
        #my_formatted_text = re.findall('"(.*?)"', str(my_formatted_text), re.S)
        #my_formatted_text = re.sub('<b>.*?</b>', '', str(my_formatted_text))
        #my_formatted_text = my_formatted_text.split(',')

        if response.error.message:
            raise Exception(
                '{}\nFor more info on error messages, check: '
                'https://cloud.google.com/apis/design/errors'.format(
                    response.error.message))
        

        ### end of vision api web detection, uncomment when ready

        # maps user comment to name of art
        art_list = Comment.objects.all()

        for art in art_list: 
            art_name = art.identifier
            art_comment = art.comment
            art_comments[art_comment] = art_name

        

        cmt_thr = ""

        for comment, name in art_comments.items():
            if name == actual_name:
                cmt_thr += comment
        print("comment thread", cmt_thr)
        
        art = language_analysis(cmt_thr)      
        art_sent = round(art.score, 2)
        art_mag = round(art.magnitude, 2)
        print(art_sent)
        print(art_mag)

    context = {
        'text': sites,
        'format_text':format_text,
        'art_sent': art_sent,
        'art_mag': art_mag,
        'actual_name': actual_name,
        'yt_vids':videos,
        'comments':comments,
        'keyword':keyword,
        'art_comment': art_comments,
        'score':sent_score,
        'magnitude':sent_mag
    }

    return render(request,"reviews/review_detail.html",context)


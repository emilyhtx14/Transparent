from django import forms
from .models import Matching, Comment

class UploadFileForm(forms.Form):
    title = forms.CharField(max_length=50)
    file = forms.FileField()

class CommentForm(forms.ModelForm):
    identifier = forms.TextInput()
    comment = forms.TextInput()
    impact = forms.DecimalField()

    class Meta:
        model = Comment
        fields = [
            'comment',
            'impact',
            'identifier'
        ]
        labels = {
            'identifier': "Type in the first three words from the keyword bank.",
            'comment': "What are your thoughts?",
            'impact':"From a scale of 1 - 10, how impactful do you think this monument is?"
        }

class MatchingForm(forms.ModelForm):
    name = forms.TextInput()
    sell_topics = forms.TextInput()
    buy_topics = forms.TextInput()
    city = forms.TextInput()
    study_topics = forms.TextInput()
    email = forms.TextInput()
    sell_price = forms.DecimalField()

    class Meta:
        model = Matching
        fields = [
            'name',
            'sell_topics',
            'buy_topics',
            'city',
            'study_topics',
            'email',
            'sell_price'
        ]
        labels = {
            'name': 'Name',
            'sell_topics':'Selling Book Areas',
            'buy_topics':'Buying Book Areas',
            'city':'City of Residence',
            'study_topics':'Group Study Possibilities',
            'email':'Enter Email',
            'sell_price': 'Selling Price'
        }
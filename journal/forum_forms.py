from django import forms
from .forum_models import ForumThread, ForumPost, NewsArticle

class ForumThreadForm(forms.ModelForm):
    class Meta:
        model = ForumThread
        fields = ['title']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Thread title',
                'maxlength': 200
            })
        }

class ForumPostForm(forms.ModelForm):
    class Meta:
        model = ForumPost
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Write your reply...',
                'rows': 4
            })
        }

class NewsArticleForm(forms.ModelForm):
    class Meta:
        model = NewsArticle
        fields = ['title', 'summary', 'link', 'published_at']

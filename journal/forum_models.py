from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class ForumThread(models.Model):
    title = models.CharField(max_length=200)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='forum_threads')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class ForumPost(models.Model):
    thread = models.ForeignKey(ForumThread, on_delete=models.CASCADE, related_name='posts')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='forum_posts')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Post by {self.author} on {self.thread}"

class NewsArticle(models.Model):
    title = models.CharField(max_length=255)
    summary = models.TextField()
    link = models.URLField()
    published_at = models.DateTimeField()

    def __str__(self):
        return self.title

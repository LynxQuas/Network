from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass
       
class Posts(models.Model):
    author = models.ForeignKey("User", blank=True, on_delete=models.CASCADE, related_name="user_posts")
    content = models.TextField(max_length=1000)
    timestamp = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField("User", blank=True, related_name="liked_posts")

    def serialize(self):
        return { 
            "id": self.id,
            "author": self.author.username,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "likes": [user.id for user in self.likes.all()]
        }

class Follow(models.Model):
    user = models.ForeignKey("User", on_delete=models.CASCADE, null=True, related_name="followers")
    following = models.ForeignKey("User", on_delete=models.CASCADE, null=True, related_name="following")

    def __str__(self):
         return f"{self.following.username} follows {self.user.username}"
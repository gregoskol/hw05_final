from django import forms

from .models import Comment, Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ("text", "group", "image")
        labels = {
            "text": "Текст",
            "group": "Группа",
            "image": "Изображение",
        }
        help_texts = {
            "text": "Текст поста",
            "group": "Группа, к которой относится пост",
            "image": "Изображение, прикрепляемое к посту",
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ("text",)
        labels = {
            "text": "Текст",
        }
        help_texts = {
            "text": "Текст комментария",
        }

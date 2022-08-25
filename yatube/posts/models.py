from core.models import CreatedModel
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import CheckConstraint, UniqueConstraint

from posts.validators import clean_post

User = get_user_model()

CUT_TEXT = 15


class Group(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()

    def __str__(self):
        return self.title


class Post(CreatedModel):
    text = models.TextField(validators=[clean_post])
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="posts"
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        related_name="posts",
        blank=True,
        null=True,
    )
    image = models.ImageField("Картинка", upload_to="posts/", blank=True)

    class Meta:
        ordering = ["-created"]
        verbose_name = "Пост"
        verbose_name_plural = "Посты"

    def __str__(self):
        return self.text[:CUT_TEXT]


class Comment(CreatedModel):
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name="comments"
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="comments"
    )
    text = models.TextField()

    class Meta:
        ordering = ["-created"]
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"


class Follow(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="follower"
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="following"
    )

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
        constraints = [
            UniqueConstraint(fields=["user", "author"], name="unique_follow"),
            CheckConstraint(
                check=~models.Q(user=models.F("author")),
                name="no_follow_myself",
            ),
        ]

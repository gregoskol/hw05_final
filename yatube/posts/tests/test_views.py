import shutil
import tempfile

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from posts.models import Comment, Follow, Group, Post

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostViewTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username="TestAuthor")
        cls.user_following = User.objects.create_user(
            username="FollowingAuthor"
        )
        cls.user_follower = User.objects.create_user(username="FollowerAuthor")
        cls.group = Group.objects.create(
            title="Тестовый заголовок группы",
            slug="test_slug",
            description="Тестовое описание группы",
        )
        cls.another_group = Group.objects.create(
            title="Тестовый заголовок группы 2",
            slug="test_slug_another",
            description="Тестовое описание группы 2",
        )
        small_gif = (
            b"\x47\x49\x46\x38\x39\x61\x02\x00"
            b"\x01\x00\x80\x00\x00\x00\x00\x00"
            b"\xFF\xFF\xFF\x21\xF9\x04\x00\x00"
            b"\x00\x00\x00\x2C\x00\x00\x00\x00"
            b"\x02\x00\x01\x00\x00\x02\x02\x0C"
            b"\x0A\x00\x3B"
        )
        uploaded = SimpleUploadedFile(
            name="small.gif", content=small_gif, content_type="image/gif"
        )
        posts = [
            Post(
                text="Текст",
                author=cls.user,
                group=cls.group,
            )
            for i in range(15)
        ]
        cls.post = Post.objects.bulk_create(posts)
        cls.post = Post.objects.create(
            text="Пост с картинкой",
            author=cls.user,
            group=cls.group,
            image=uploaded,
        )
        cls.comment = Comment.objects.create(
            text="Комментарий",
            author=cls.user,
            post=cls.post,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        cache.clear()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_client_following = Client()
        self.authorized_client_following.force_login(self.user_following)
        self.authorized_client_follower = Client()
        self.authorized_client_follower.force_login(self.user_follower)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            reverse("posts:index"): "posts/index.html",
            reverse(
                "posts:group_list", kwargs={"slug": "test_slug"}
            ): "posts/group_list.html",
            reverse(
                "posts:profile", kwargs={"username": "TestAuthor"}
            ): "posts/profile.html",
            reverse(
                "posts:post_detail", kwargs={"post_id": 1}
            ): "posts/post_detail.html",
            reverse(
                "posts:post_edit", kwargs={"post_id": 1}
            ): "posts/create_post.html",
            reverse("posts:post_create"): "posts/create_post.html",
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_page_with_form_show_correct_context(self):
        """Шаблоны create, edit сформированы с правильным контекстом."""
        response_form_fields = {
            self.authorized_client.get(
                reverse("posts:post_edit", kwargs={"post_id": 1})
            ): ("text", forms.fields.CharField),
            self.authorized_client.get(reverse("posts:post_create")): (
                "group",
                forms.fields.ChoiceField,
            ),
        }
        for response, expected in response_form_fields.items():
            with self.subTest(response=response):
                form_field = response.context.get("form").fields.get(
                    expected[0]
                )
                self.assertIsInstance(form_field, expected[1])

    def test_page_with_paginator_show_correct_context(self):
        """Шаблоны index, group_list, profile сформированы с правильным
        контекстом, проверка Paginator.
        """
        user = self.authorized_client
        urls = {
            "posts:index": "",
            "posts:group_list": {"slug": "test_slug"},
            "posts:profile": {"username": "TestAuthor"},
        }
        user = self.authorized_client
        paginator_test_addr = "?page=2"
        for url, kwargs in urls.items():
            with self.subTest(url=url):
                response = user.get(
                    reverse(url, kwargs=kwargs) + paginator_test_addr
                )
                self.assertEqual(len(response.context["page_obj"]), 6)
                response = user.get(reverse(url, kwargs=kwargs))
                self.assertEqual(len(response.context["page_obj"]), 10)
                first_object = response.context["page_obj"][0]
                objects = {
                    first_object.text: "Пост с картинкой",
                    first_object.author: self.user,
                    first_object.group: self.group,
                    first_object.image.name: "posts/small.gif",
                }
                for object, expected in objects.items():
                    with self.subTest(object=object):
                        self.assertEqual(object, expected)

    def test_post_detail_pages_show_correct_context(self):
        """Проверка отображения созданного поста на нужных страницах."""
        user = self.authorized_client
        self.post_check = Post.objects.create(
            text="Текст",
            author=self.user,
            group=self.group,
        )
        responses = [
            user.get(reverse("posts:index")),
            user.get(
                reverse("posts:group_list", kwargs={"slug": "test_slug"})
            ),
            user.get(
                reverse("posts:profile", kwargs={"username": "TestAuthor"})
            ),
        ]
        for response in responses:
            self.assertIn(self.post_check, response.context["page_obj"])
        response = user.get(
            reverse("posts:group_list", kwargs={"slug": "test_slug_another"})
        )
        self.assertNotIn(self.post_check, response.context["page_obj"])

    def test_post_detail_pages_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse("posts:post_detail", kwargs={"post_id": 16})
        )
        self.assertEqual(response.context.get("post").text, "Пост с картинкой")
        self.assertEqual(response.context.get("post").author, self.user)
        self.assertEqual(response.context.get("post").group, self.group)
        self.assertEqual(
            response.context.get("post").image.name, "posts/small.gif"
        )
        self.assertIn(self.comment, response.context.get("comments"))

    def test_cache_index_page_correct(self):
        """Шаблон index кешируется."""
        self.post_cache = Post.objects.create(
            text="Пост для проверки кеша",
            author=self.user,
        )
        response = self.authorized_client.get(reverse("posts:index"))
        self.assertIn(self.post_cache, response.context["page_obj"])
        Post.objects.filter(id=self.post_cache.id).delete()
        response_after_del = self.authorized_client.get(reverse("posts:index"))
        self.assertEqual(response.content, response_after_del.content)
        cache.clear()
        response_after_clear = self.authorized_client.get(
            reverse("posts:index")
        )
        self.assertNotEqual(
            response_after_clear.content, response_after_del.content
        )

    def test_follow_unfollow(self):
        """Проверка возможности подписки/отписки."""
        self.authorized_client_follower.get(
            reverse(
                "posts:profile_follow",
                kwargs={"username": self.user_following.username},
            )
        )
        self.assertEqual(Follow.objects.all().count(), 1)
        self.authorized_client_follower.get(
            reverse(
                "posts:profile_unfollow",
                kwargs={"username": self.user_following.username},
            )
        )
        self.assertEqual(Follow.objects.all().count(), 0)

    def test_follow_correct_context(self):
        """Проверка отображения поста с учетом подписок."""
        self.follow_check = Follow.objects.create(
            user=self.user_follower,
            author=self.user_following,
        )
        self.post_follow_check = Post.objects.create(
            text="Пост проверки подписок",
            author=self.user_following,
        )
        response = self.authorized_client_follower.get(
            reverse("posts:follow_index")
        )
        self.assertIn(self.post_follow_check, response.context["page_obj"])
        response = self.authorized_client.get(reverse("posts:follow_index"))
        self.assertNotIn(self.post_follow_check, response.context["page_obj"])

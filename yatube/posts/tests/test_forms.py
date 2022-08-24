import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from posts.models import Comment, Group, Post

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username="TestAuthor")
        cls.group = Group.objects.create(
            title="Тестовый заголовок группы",
            slug="test_slug",
            description="Тестовое описание группы",
        )
        cls.post = Post.objects.create(
            text="Редактируемый текст",
            author=cls.user,
            group=cls.group,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        posts_count = Post.objects.count()
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
        form_data = {
            "text": "Текст",
            "author": self.user.id,
            "group": self.group.id,
            "image": uploaded,
        }
        response = self.authorized_client.post(
            reverse("posts:post_create"), data=form_data, follow=True
        )

        self.assertRedirects(
            response,
            reverse("posts:profile", kwargs={"username": "TestAuthor"}),
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text=form_data["text"],
                author=form_data["author"],
                group=form_data["group"],
            ).exists()
        )
        self.assertTrue(
            Post.objects.filter(
                text=form_data["text"],
                author=form_data["author"],
                group=form_data["group"],
            ).latest("created")
        )
        check_image = Post.objects.latest("created")
        self.assertEqual(check_image.image.name, "posts/small.gif")

    def test_edit_post(self):
        """Валидная форма редактирует запись в Post."""
        posts_count = Post.objects.count()
        form_data = {
            "text": "Отредактированный текст",
            "author": self.user.id,
            "group": self.group.id,
        }
        response = self.authorized_client.post(
            reverse("posts:post_edit", kwargs={"post_id": 1}),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(
            response, reverse("posts:post_detail", kwargs={"post_id": 1})
        )
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertTrue(
            Post.objects.filter(
                text=form_data["text"],
                author=form_data["author"],
                group=form_data["group"],
            ).exists()
        )

    def test_create_comment(self):
        """Валидная форма создает запись в Comment, требуется авторизация."""
        comments_count = Comment.objects.count()
        form_data = {
            "text": "Комментарий",
            "author": self.user.id,
        }
        response = self.guest_client.post(
            reverse("posts:add_comment", kwargs={"post_id": 1}),
            data=form_data,
            follow=True,
        )
        self.assertEqual(Comment.objects.count(), comments_count)
        response = self.authorized_client.post(
            reverse("posts:add_comment", kwargs={"post_id": 1}),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(
            response,
            reverse("posts:post_detail", kwargs={"post_id": 1}),
        )
        self.assertEqual(Comment.objects.count(), comments_count + 1)

from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase
from posts.models import Group, Post

User = get_user_model()


class PostURLTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username="TestAuthor")
        cls.another_user = User.objects.create_user(username="TestNotAuthor")
        cls.group = Group.objects.create(
            title="Тестовый заголовок группы",
            slug="test_slug",
            description="Тестовое описание группы",
        )
        cls.post = Post.objects.create(
            text="Текст",
            author=cls.user,
            group=cls.group,
        )

    def setUp(self):
        cache.clear()
        self.guest_client = Client()
        self.authorized_client = Client()
        self.not_author_authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.not_author_authorized_client.force_login(self.another_user)

    def test_urls_exists_for_auth_user(self):
        """Доступность адресов авторизованному пользователю."""
        url_names = [
            "/create/",
            "/posts/1/edit/",
        ]
        for address in url_names:
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_exists_for_guest(self):
        """Доступность адресов неавторизованному пользователю."""
        url_names = [
            "/",
            "/group/test_slug/",
            "/profile/TestAuthor/",
            "/posts/1/",
        ]
        for address in url_names:
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_exists_404(self):
        """Ошибка 404."""
        response = self.guest_client.get("/unexisting_page/")
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_urls_redirect(self):
        """Перенаправление гостя с /create/ и не автора с /edit/."""
        url_names = {
            "/create/": (self.guest_client, "/auth/login/?next=/create/"),
            "/posts/1/edit/": (self.not_author_authorized_client, "/posts/1/"),
        }
        for address, client_redirect in url_names.items():
            with self.subTest(address=address):
                response = client_redirect[0].get(address, follow=True)
                self.assertRedirects(response, client_redirect[1])

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            "/": "posts/index.html",
            "/group/test_slug/": "posts/group_list.html",
            "/profile/TestAuthor/": "posts/profile.html",
            "/posts/1/": "posts/post_detail.html",
            "/create/": "posts/create_post.html",
            "/posts/1/edit/": "posts/create_post.html",
            "/unexpected/": "core/404.html",
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

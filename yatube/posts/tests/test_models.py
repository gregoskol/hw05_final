from django.contrib.auth import get_user_model
from django.test import TestCase
from posts.models import Group, Post

User = get_user_model()

CUT_TEXT = 15
MULT_TEXT = 4


class PostModelTest(TestCase):
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
            text="Текст" * MULT_TEXT,
            author=cls.user,
            group=cls.group,
        )

    def test_correct_str(self):
        """Проверяем, что у моделей корректно работает __str__."""
        field_str_texts = {
            PostModelTest.post: PostModelTest.post.text[:CUT_TEXT],
            PostModelTest.group: PostModelTest.group.title,
        }
        for field, expected_value in field_str_texts.items():
            with self.subTest(field=field):
                self.assertEqual(str(field), expected_value)

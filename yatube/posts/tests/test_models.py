from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовая группа',
        )

    def test_group_post_model_has_correct_object_names(self):
        expected_title = self.group.title
        self.assertEqual(expected_title, str(self.group))

    def test_post_model_has_correct_object_names(self):
        expected_title = self.post.text[:15]
        self.assertEqual(expected_title, str(self.post))

    def test_post_verbose_name(self):
        field_verboses = {
            'text': 'Новый пост',
            'pub_date': 'Дата публикации',
            'author': 'Автор',
            'group': 'Группа',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    self.post._meta.get_field(field).verbose_name,
                    expected_value,
                )

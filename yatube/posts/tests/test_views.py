import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..forms import PostForm
from ..models import Comment, Follow, Group, Post

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.user1 = User.objects.create_user(username='auth1')
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.small_jpeg = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.image = SimpleUploadedFile(
            name='small.jpeg',
            content=cls.small_jpeg,
            content_type='image/jpeg',
        )
        cls.post = Post.objects.create(
            text='Тестовый заголовок',
            author=cls.user,
            group=cls.group,
            image=cls.image,
        )
        cls.comment = Comment.objects.create(
            text='Тестовый комментарий',
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
        self.list_expected = [
            self.post.text,
            self.post.author,
            self.post.group,
            self.post.image,
        ]

    def test_pages_uses_correct_template(self):
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_lists', kwargs={'slug': self.group.slug}
            ): 'posts/group_list.html',
            reverse(
                'posts:profile', kwargs={'username': self.user.username}
            ): 'posts/profile.html',
            reverse(
                'posts:post_detail', kwargs={'post_id': self.post.id}
            ): 'posts/post_detail.html',
            reverse(
                'posts:post_edit', kwargs={'post_id': self.post.id}
            ): 'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html',
        }

        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def _assertListEqual(self, list_result):
        return self.assertListEqual(self.list_expected, list_result)

    def test_index_shows_correct_context(self):
        response = self.client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.text
        post_author_0 = first_object.author
        post_group_0 = first_object.group
        post_image_0 = first_object.image
        list_result = [post_text_0, post_author_0, post_group_0, post_image_0]
        self._assertListEqual(list_result)

    def test_group_lists_shows_correct_context(self):
        response = self.client.get(
            reverse('posts:group_lists', kwargs={'slug': self.group.slug})
        )
        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.text
        post_author_0 = first_object.author
        post_group_0 = first_object.group
        post_image_0 = first_object.image
        list_result = [post_text_0, post_author_0, post_group_0, post_image_0]
        self._assertListEqual(list_result)

    def test_profile_shows_correct_context(self):
        response = self.client.get(
            reverse('posts:profile', kwargs={'username': self.user.username})
        )
        post = response.context.get('post')
        author = response.context.get('author')
        self.assertEqual(author, self.post.author)
        self.assertEqual(post.image, self.post.image)

    def test_post_detail_shows_correct_context(self):
        response = self.client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.pk})
        )
        post_object_detail = response.context.get('post')
        post_text = post_object_detail.text
        post_author = post_object_detail.author
        post_group = post_object_detail.group
        post_image = post_object_detail.image
        post_comment_0 = post_object_detail.comments.last().text
        list_result = [post_text, post_author, post_group, post_image]
        self._assertListEqual(list_result)
        self.assertEqual(post_comment_0, self.comment.text)

    def test_post_create_shows_correct_context(self):
        response = self.authorized_client.get(reverse('posts:post_create'))
        self.assertIsInstance(response.context.get('form'), PostForm)
        self.assertFalse(response.context['is_edit'])

    def test_post_edit_shows_correct_context(self):
        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': self.post.pk})
        )
        self.assertIsInstance(response.context.get('form'), PostForm)
        self.assertTrue(response.context['is_edit'])

    def test_index_post_with_group(self):
        response = self.client.get(reverse('posts:index'))
        self.assertIn(self.post, response.context.get('page_obj'))

    def test_group_lists_with_group(self):
        response = self.client.get(
            reverse('posts:group_lists', kwargs={'slug': self.group.slug})
        )
        self.assertIn(self.post, response.context.get('page_obj'))

    def test_profile_with_group(self):
        response = self.client.get(
            reverse('posts:profile', kwargs={'username': self.user.username})
        )
        self.assertIn(self.post, response.context.get('page_obj'))

    def test_index_caches_posts(self):
        response = self.client.get(reverse('posts:index'))
        last_post = Post.objects.last()
        last_post.delete()
        self.assertIn(bytes(last_post.text, 'UTF-8'), response.content)
        cache.clear()
        response = self.client.get(reverse('posts:index'))
        self.assertNotIn(bytes(last_post.text, 'UTF-8'), response.content)

    def test_profile_follow_works(self):
        follow_count = Follow.objects.filter(user=self.user).count()
        self.authorized_client.get(
            reverse(
                'posts:profile_follow',
                kwargs={'username': self.user1.username},
            )
        )
        self.assertEqual(Follow.objects.count(), follow_count + 1)

    def test_profile_unfollow_works(self):
        Follow.objects.create(
            user=self.user,
            author=self.user1,
        )
        follow_count = Follow.objects.filter(user=self.user).count()
        self.authorized_client.get(
            reverse(
                'posts:profile_unfollow',
                kwargs={'username': self.user1.username},
            )
        )
        self.assertEqual(Follow.objects.count(), follow_count - 1)

    def test_follow_index_works(self):
        post = Post.objects.create(
            text='Текст нового поста',
            author=self.user1,
        )
        response = self.authorized_client.get(reverse('posts:follow_index'))
        self.assertNotIn(post, response.context.get('page_obj'))
        self.authorized_client.get(
            reverse(
                'posts:profile_follow',
                kwargs={'username': self.user1.username},
            )
        )
        response1 = self.authorized_client.get(reverse('posts:follow_index'))
        self.assertIn(post, response1.context.get('page_obj'))


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post_group = Post.objects.bulk_create(
            [
                Post(
                    text='Тестовый заголовок',
                    author=cls.user,
                    group=cls.group,
                ),
            ]
            * (settings.POSTS_PER_PAGE + 3)
        )

    def setUp(self):
        cache.clear()

    def _page_count(self, response, response1):
        page_count = {
            response: settings.POSTS_PER_PAGE,
            response1: len(self.post_group) - settings.POSTS_PER_PAGE,
        }
        return page_count

    def test_index_pages_contains_correct_num_of_records(self):
        response = self.client.get(reverse('posts:index'))
        response1 = self.client.get(reverse('posts:index') + '?page=2')
        page_count = self._page_count(response, response1)
        for answer, pages in page_count.items():
            with self.subTest(answer=answer):
                self.assertEqual(len(answer.context['page_obj']), pages)

    def test_group_lists_pages_contains_correct_num_of_records(self):
        response = self.client.get(
            reverse('posts:group_lists', kwargs={'slug': self.group.slug})
        )
        response1 = self.client.get(
            reverse('posts:group_lists', kwargs={'slug': self.group.slug})
            + '?page=2'
        )
        page_count = self._page_count(response, response1)
        for answer, pages in page_count.items():
            with self.subTest(answer=answer):
                self.assertEqual(len(answer.context['page_obj']), pages)

    def test_profile_pages_contains_correct_num_of_records(self):
        response = self.client.get(
            reverse('posts:profile', kwargs={'username': self.user.username})
        )
        response1 = self.client.get(
            reverse('posts:profile', kwargs={'username': self.user.username})
            + '?page=2'
        )
        page_count = self._page_count(response, response1)
        for answer, pages in page_count.items():
            with self.subTest(answer=answer):
                self.assertEqual(len(answer.context['page_obj']), pages)

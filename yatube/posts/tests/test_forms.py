from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.cache import cache

from posts.models import Group, Post, User, Comment

POST_CREATE = reverse('posts:post_create')
small_gif = (
    b'\x47\x49\x46\x38\x39\x61\x02\x00'
    b'\x01\x00\x80\x00\x00\x00\x00\x00'
    b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
    b'\x00\x00\x00\x2C\x00\x00\x00\x00'
    b'\x02\x00\x01\x00\x00\x02\x02\x0C'
    b'\x0A\x00\x3B'
)


class PostFormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='NoName')
        cls.group = Group.objects.create(
            title='test_title',
            description='test_description',
            slug='test-slug'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            text='test_post',
            author=cls.author,
            group=cls.group,
            image=cls.uploaded,
        )
        cls.POST_EDIT = reverse('posts:post_edit', args=({cls.post.id}))

    def setUp(self):
        cache.clear()
        self.user = User.objects.create_user(username='User')
        self.anonim_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.author)

    def test_create_post_anonim(self):
        """аноним не может создать пост"""
        posts_count = Post.objects.count()

        form_data = {
            'text': 'Тестовый текст',
            'group': self.group.id,
            'image': self.uploaded
        }

        response = self.anonim_client.post(
            POST_CREATE,
            data=form_data,
            follow=True,
        )

        self.assertEqual(Post.objects.count(), posts_count)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        posts_count = Post.objects.count()

        form_data = {
            'text': 'Тестовый текст',
            'group': self.group.id,

        }

        response = self.authorized_client.post(
            POST_CREATE,
            data=form_data,
            follow=True
        )

        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertEqual(response.status_code, HTTPStatus.OK)

        last_post = Post.objects.order_by('-id')[0]

        self.assertEqual(last_post.text, form_data['text'])
        self.assertEqual(last_post.author, self.author)

    def test_edit_post_anonim(self):
        """аноним не может отредактировать пост"""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Отредактированный текст',
            'group': self.group.id,
        }

        self.anonim_client.post(
            self.POST_EDIT,
            data=form_data,
            follow=True
        )

        self.assertEqual(Post.objects.count(), posts_count)
        self.assertTrue(not Post.objects.filter(
            text='Отредактированный текст').count())

    def test_edit_post(self):
        """Валидная форма редактирует пост"""
        posts_count = Post.objects.count()
        POST_DETAIL = reverse("posts:post_detail",
                              kwargs={"post_id": self.post.id})
        form_data = {
            'text': 'Отредактированный текст',
            'group': self.group.id,
        }

        response = self.authorized_client.post(
            self.POST_EDIT,
            data=form_data,
            follow=True
        )

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(response, POST_DETAIL)
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertTrue(Post.objects.filter(
            text='Отредактированный текст').count())

        last_post = Post.objects.order_by('-id')[0]

        self.assertEqual(last_post.text, form_data['text'])
        self.assertEqual(last_post.author, self.author)


class CommentFormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author_post = User.objects.create_user(username='author_post')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.author_post,
            text='Тестовый пост',
        )
        cls.ADD_COMMENT = reverse('posts:add_comment',
                                  kwargs={'post_id': cls.post.pk})

    def setUp(self):
        cache.clear()
        self.user = User.objects.create_user(username='User')
        self.anonim_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_comment_anonim(self):
        """аноним не может создать комментарий"""
        comments_count = Comment.objects.count()

        form_data = {
            'text': 'Тестовый текст комментария',
        }

        response = self.anonim_client.post(
            self.ADD_COMMENT,
            data=form_data,
            follow=True,
        )

        self.assertEqual(Comment.objects.count(), comments_count)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_create_comment(self):
        """Валидная форма создает запись в Comment."""
        comments_count = Comment.objects.count()

        form_data = {
            'text': 'Тестовый текст комментария',
        }
        response = self.authorized_client.post(
            self.ADD_COMMENT,
            data=form_data,
            follow=True,
        )

        self.assertEqual(Comment.objects.count(), comments_count + 1)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        last_comment = Comment.objects.order_by('-id')[0]
        self.assertEqual(last_comment.text, form_data['text'])
        self.assertEqual(last_comment.author, self.user)

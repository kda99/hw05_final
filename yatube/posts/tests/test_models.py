from django.test import TestCase

from posts.models import Group, Post, User, Comment, Follow


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        post = PostModelTest.post
        self.assertEqual(post.text[:15], str(post),
                         'некорректно работает Post.__str__()')
        group = PostModelTest.group
        self.assertEqual(group.title, str(group),
                         'некорректно работает Group.__str__()')

    def test_verbose_name(self):
        post = PostModelTest.post
        self.assertEqual(post._meta.get_field(
            'text').verbose_name, 'Текст'
            ' поста', 'некорректно работает Group verbose_name Post')

    def test_help_text(self):
        post = PostModelTest.post
        self.assertEqual(post._meta.get_field(
            'text').help_text, 'Введите текст'
            ' поста', 'некорректно работает help_text Group')


class CommentModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.author_comment = User.objects.create_user(
            username='author_comment')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.author_comment,
            text='Тестовый комментарий',
        )

    def test_verbose_name(self):
        comment = CommentModelTest.comment
        self.assertEqual(comment._meta.get_field('text').verbose_name,
        'Текст комментария', 'некорректно работает verbose_name Comment')

    def test_help_text(self):
        comment = CommentModelTest.comment
        self.assertEqual(comment._meta.get_field(
            'text').help_text, 'Введите текст'
            ' комментария', 'некорректно работает help_text Comment')


class FollowModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='author')
        cls.follower = User.objects.create_user(username='follower')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.author,
            text='Тестовый пост',
        )
        cls.follow = Follow.objects.create(
            user=cls.follower,
            author=cls.author
        )

    def test_verbose_name(self):
        follow = FollowModelTest.follow
        self.assertEqual(follow._meta.verbose_name,
        'Подписка', 'некорректно работает verbose_name Follow')

    def test_verbose_name_plural(self):
        follow = FollowModelTest.follow
        self.assertEqual(follow._meta.verbose_name_plural,
        'Подписки', 'некорректно работает verbose_name Follow')

from django.test import TestCase, Client
from django.urls import reverse
from django.core.cache import cache

from ..models import Group, Post, User

INDEX = reverse('posts:index')
POST_CREATE = reverse('posts:post_create')


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='author')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            text='Тестовый пост',
            author=cls.author,
            group=cls.group,
        )
        cls.user = User.objects.create_user(username='HasNoName')

    def setUp(self):
        cache.clear()
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client_author = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_client_author.force_login(self.author)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        GROUP_LIST = reverse('posts:group_list', kwargs={'slug': self.group.slug})
        PROFILE = reverse('posts:profile', kwargs={'username': self.author})
        POST_EDIT = reverse('posts:post_edit', kwargs={'post_id': self.post.pk})
        POST_DETAIL = reverse('posts:post_detail', kwargs={'post_id': self.post.pk})
        FOLLOW_INDEX = reverse('posts:follow_index', None)
        ADD_COMMENT = reverse('posts:add_comment', kwargs={'post_id': self.post.pk})
        PROFILE_FOLLOW = reverse('posts:profile_follow', kwargs={'username': self.author.username})
        PROFILE_UNFOLLOW = reverse('posts:profile_unfollow', kwargs={'username': self.author.username})
        templates_url_names = {
            INDEX: 'posts/index.html',
            GROUP_LIST: 'posts/group_list.html',
            PROFILE: 'posts/profile.html',
            POST_EDIT: 'posts/create_post.html',
            POST_DETAIL: 'posts/post_detail.html',
            POST_CREATE: 'posts/create_post.html',
            '/1': 'core/404.html',
            # ADD_COMMENT: 'posts/post_detail.html',
            FOLLOW_INDEX: 'posts/follow.html',
            # PROFILE_FOLLOW: 'posts/profile.html',
            # PROFILE_UNFOLLOW: 'posts/profile.html',
        }

        for address, template in templates_url_names.items():
            if address not in (POST_EDIT,
                               PROFILE_FOLLOW,
                               FOLLOW_INDEX,
                               ADD_COMMENT,
                               PROFILE_UNFOLLOW,
                               POST_CREATE):
                with self.subTest(address=address):
                    response = self.guest_client.get(address)
                    self.assertTemplateUsed(response, template)

        for address, template in templates_url_names.items():
            if address not in (POST_EDIT,):
                with self.subTest(address=address):
                    response = self.authorized_client.get(address)
                    self.assertTemplateUsed(response, template)

        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client_author.get(address)
                self.assertTemplateUsed(response, template)

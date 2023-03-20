from django.db.models.query import QuerySet
from rest_framework import filters, mixins, viewsets
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated

from api.serializers import (
    CommentSerializer,
    FollowSerializer,
    GroupSerializer,
    PostSerializer,
)
from posts.models import Group, Post

from api.permissions import OwnerOrReadOnlyPermission


class CreateListRetrieveViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    pass


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    pagination_class = LimitOffsetPagination
    permission_classes = (
        OwnerOrReadOnlyPermission,
    )

    def perform_create(self, serializer: PostSerializer) -> None:
        serializer.save(author=self.request.user)


class GroupViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer


class CommentViewSet(viewsets.ModelViewSet):
    permission_classes = (
        OwnerOrReadOnlyPermission,
    )
    serializer_class = CommentSerializer

    def perform_create(self, serializer: CommentSerializer) -> None:
        post_id = self.kwargs.get('post_id')
        post = get_object_or_404(
            Post,
            pk=post_id,
        )
        serializer.save(
            author=self.request.user,
            post=post,
        )

    def get_queryset(self) -> QuerySet:
        post_id = self.kwargs.get('post_id')
        post = get_object_or_404(
            Post,
            pk=post_id,
        )
        comments_queryset = post.comments.all()
        return comments_queryset


class FollowViewSet(CreateListRetrieveViewSet):
    serializer_class = FollowSerializer
    permission_classes = (
        OwnerOrReadOnlyPermission,
        IsAuthenticated,
    )
    filter_backends = (
        filters.SearchFilter,
    )
    search_fields = (
        'user__username',
        'following__username',
    )

    def get_queryset(self) -> QuerySet:
        return self.request.user.follower.all()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

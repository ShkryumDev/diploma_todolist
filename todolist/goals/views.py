from django.db import transaction
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, permissions

from rest_framework.filters import OrderingFilter, SearchFilter

from todolist.goals.filters import GoalDateFilter
from todolist.goals.models import GoalCategory, Goal, GoalComment, BoardParticipant, Board
from todolist.goals.permissions import GoalCategoryPermissions, BoardPermissions
from todolist.goals.serializers import GoalCategoryCreateSerializer, GoalCategorySerializer, GoalCreateSerializer, \
    GoalSerializer, GoalCommentSerializer, GoalCommentCreateSerializer, BoardCreateSerializer, BoardListSerializer


class BoardCreateView(generics.CreateAPIView):
    serializer_class = BoardCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        BoardParticipant.objects.create(user=self.request.user, board=serializer.save())


class BoardListView(generics.ListAPIView):
    serializer_class = BoardListSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [OrderingFilter]
    ordering = ['title']

    def get_queryset(self):
        return Board.objects.prefetch_related('participants__user').filter(participants__user_id=self.request.user_id,
                                                                           is_deleted=False)


class BoardView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [BoardPermissions]
    serializer_class = BoardListSerializer

    def get_queryset(self):
        return Board.objects.prefetch_related('participants__user').filter(is_deleted=False)

    def perform_destroy(self, instance: Board) -> None:
        with transaction.atomic():
            Board.objects.filter(id=instance.id).update(is_deleted=True)
            instance.categories.update(is_deleted=True)
            Goal.objects.filter(category__board=instance).update(status=Goal.Status.archived)


class GoalCategoryCreateView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = GoalCategoryCreateSerializer


class GoalCategoryListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = GoalCategorySerializer
    filter_backends = [OrderingFilter, SearchFilter]
    ordering_fields = ('title', 'created')
    ordering = ['title']
    search_fields = ['title']

    def get_queryset(self):
        return GoalCategory.objects.prefetch_related('goals').filter(user=self.request.user, is_deleted=False)


class GoalCategoryView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [GoalCategoryPermissions]
    serializer_class = GoalCategorySerializer

    def get_queryset(self):
        return GoalCategory.objects.select_related('user').filter(user=self.request.user, is_deleted=False)

    def perform_destroy(self, instance: GoalCategory) -> None:
        with transaction.atomic():
            instance.is_deleted = True
            instance.save(update_fields=('is_deleted',))
            instance.goals.update(status=Goal.Status.archived)


class GoalCreateView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = GoalCreateSerializer


class GoalListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = GoalSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_class = GoalDateFilter
    ordering_fields = ('title', 'created')
    ordering = ['title']
    search_fields = ['title', 'description']

    def get_queryset(self):
        return (
            Goal.objects.prefetch_related('comments').select_related('category').filter(user=self.request.user,
                                                                                        category__is_deleted=False).exclude(
                status=Goal.Status.archived)
        )


class GoalView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = GoalSerializer

    def get_queryset(self):
        return (
            Goal.objects.select_related('user').filter(user=self.request.user, category__is_deleted=False).exclude(
                status=Goal.Status.archived)
        )

    def perform_destroy(self, instance: Goal):
        instance.status = Goal.Status.archived
        instance.save(update_fields=('status',))


class GoalCommentCreateView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = GoalCommentCreateSerializer


class GoalCommentListView(generics.ListAPIView):
    model = GoalComment
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = GoalCommentSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['goal']
    ordering = ['created']

    def get_queryset(self):
        return GoalComment.objects.filter(user_id=self.request.user.id).select_related('user', 'goal')


class GoalCommentView(generics.RetrieveUpdateDestroyAPIView):
    model = GoalComment
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = GoalCommentSerializer

    def get_queryset(self):
        return GoalComment.objects.filter(user_id=self.request.user.id)

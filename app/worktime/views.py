"""Views for the worktime"""


from rest_framework import mixins, generics, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from worktime.serializers import (
    ShiftSerializer,
    WorkDayDetailsSerializer,
    WorkDaySerializer,
)
from worktime.models import Shift, WorkDay


class BaseViewAPI(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(owner=self.request.user)


class ShiftViewAPI(BaseViewAPI):
    serializer_class = ShiftSerializer
    queryset = Shift.objects.all()


class WorkDayViewAPI(BaseViewAPI):
    serializer_class = WorkDayDetailsSerializer
    queryset = WorkDay.objects.all()

    def get_serializer(self, *args, **kwargs):
        if self.action == "list":
            self.serializer_class = WorkDaySerializer

        return super().get_serializer(*args, **kwargs)

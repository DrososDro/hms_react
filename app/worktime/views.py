"""Views for the worktime"""


from rest_framework import mixins, generics, viewsets, views
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from worktime.serializers import (
    ShiftSerializer,
    WorkCaclulatorSerializer,
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


# TODO: Need Tests
class WorkDayCalculate(views.APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        res = WorkCaclulatorSerializer(data=request.data)
        if res.is_valid():
            start, end = res.data.values()

        query = WorkDay.objects.filter(
            owner=self.request.user, date__gte=start
        ).exclude(date__gt=end)

        # (0, "Normal"),
        # (1, "Weekend"),
        # (2, "Times off"),
        # (3, "Sick leave"),
        # (4, "Public holiday"),
        # (5, "Job Travel"),

        query_0 = query.filter(day=0)
        late_for_work = 0
        overtime = 0
        early_leave = 0

        for i in query_0:
            if i.before_work > 0:
                late_for_work += i.before_work
            if i.after_work >= 15:
                overtime += i.after_work
            if i.after_work < 0:
                early_leave += i.after_work

        data = {
            "late_for_work": late_for_work,
            "overtime": overtime,
            "early_leave": early_leave,
            "workdays": query_0.count(),
            "weekend": query.filter(day=1).count(),
            "times_off": query.filter(day=2).count(),
            "sick_leaves": query.filter(day=3).count(),
            "publick_holidays": query.filter(day=4).count(),
            "job_travel": query.filter(day=5).count(),
        }

        return Response(data=data)

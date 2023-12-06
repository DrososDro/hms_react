from django.urls import include, path
from rest_framework.routers import DefaultRouter
from worktime import views


app_name = "worktime"

router = DefaultRouter()
router.register("shift", views.ShiftViewAPI)
router.register("workday", views.WorkDayViewAPI)

urlpatterns = [
    path("", include(router.urls), name="shift"),
    path("workCalc/", views.WorkDayCalculate.as_view(), name="work_calc"),
]

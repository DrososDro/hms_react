"""Serializers for the work time app"""

from rest_framework import serializers
from functools import partial
from datetime import date, datetime
from worktime.models import Shift, WorkDay


class ShiftSerializer(serializers.ModelSerializer):
    """Shift serializers"""

    class Meta:
        model = Shift
        fields = ["start_of_shift", "end_of_shift", "id"]
        read_only_fields = ["id"]

    def create(self, validated_data):
        user = self.context["request"].user
        shift = Shift.objects.create(**validated_data, owner=user)
        return shift


# TODO: test for UniqueTogetherValidator
class WorkDaySerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkDay
        fields = [
            "day",
            "start_of_work",
            "end_of_work",
            "id",
            "date",
            "comment",
            "shift",
        ]
        read_only_fields = ["id"]

    def create(self, validated_data):
        if validated_data["day"] == 0:
            date_today = date.today()
            date_func = partial(
                datetime.combine,
                date_today,
            )
            shift = validated_data["shift"]
            start_of_work = validated_data.get("start_of_work")
            end_of_work = validated_data.get("end_of_work")
            before_work = date_func(start_of_work) - date_func(shift.start_of_shift)
            after = date_func(end_of_work) - date_func(shift.end_of_shift)
            validated_data["before_work"] = int(before_work.total_seconds() / 60)
            validated_data["after_work"] = int(after.total_seconds() / 60)

        data = WorkDay.objects.create(
            **validated_data,
            owner=self.context["request"].user,
        )
        return data

    def validate(self, data):
        user = self.context["request"].user
        start = data.get("start_of_work")
        end = data.get("end_of_work")
        if WorkDay.objects.filter(owner=user, date=data["date"]).exists():
            raise serializers.ValidationError(
                "Please Select another Date This already exists"
            )

        day = data.get("day")
        if day == 0 and (start is None or end is None):
            raise serializers.ValidationError(
                "Normal day should have (start of work) and (end of work)"
            )
        if day == 5:
            if start is None:
                raise serializers.ValidationError(
                    "start of work mustn't be empty",
                )
            data["end_of_work"] = None

        return super().validate(data)


# TODO: later delete this serializers it no need at all
class WorkDayDetailsSerializer(WorkDaySerializer):
    class Meta(WorkDaySerializer.Meta):
        fields = WorkDaySerializer.Meta.fields + ["comment", "shift"]


class WorkCaclulatorSerializer(serializers.Serializer):
    """Calculate the work timed of an employ"""

    from_date = serializers.DateField()
    to_date = serializers.DateField()

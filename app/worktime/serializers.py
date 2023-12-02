"""Serializers for the work time app"""

from rest_framework import serializers, validators
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
        fields = ["day", "start_of_work", "end_of_work", "id", "date"]
        read_only_fields = ["id"]

    def create(self, validated_data):
        return WorkDay.objects.create(
            **validated_data,
            owner=self.context["request"].user,
        )

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


class WorkDayDetailsSerializer(WorkDaySerializer):
    class Meta(WorkDaySerializer.Meta):
        fields = WorkDaySerializer.Meta.fields + ["comment", "shift"]

from rest_framework import serializers
import datetime as dt
from .models import Cat, Owner, Achievement, AchievementCat
import webcolors


class OwnerSerializer(serializers.ModelSerializer):
    cats = serializers.StringRelatedField(many=True, read_only=True)
    
    class Meta:
        model = Owner
        fields = ('first_name', 'last_name', 'cats')


class AchievementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Achievement
        fields = ('id', 'name')


class Hex2NameColor(serializers.Field):
    def to_representation(self, value):
        """Возвращаем название цвета."""
        return value

    def to_internal_value(self, data):
        """Конвертируем hex представление в название цвета."""
        try:
            data = webcolors.hex_to_name(hex_value=data)
        except ValueError:
            raise serializers.ValidationError('Для этого цвета нет имени')
        return data


class CatSerializer(serializers.ModelSerializer):
    achievements = AchievementSerializer(many=True, required=False)
    age = serializers.SerializerMethodField()
    color = Hex2NameColor()

    class Meta:
        model = Cat
        fields = ('id', 'name', 'color', 'birth_year', 'owner', 'achievements', 'age')

    def get_age(self, obj):
        return dt.datetime.now().year - obj.birth_year

    def create(self, validated_data):
        if 'achievements' not in self.initial_data:
            cat = Cat.objects.create(**validated_data)
            return cat
        achievements = validated_data.pop('achievements')
        cat = Cat.objects.create(**validated_data)
        for achievement in achievements:
            current_achievement, status = Achievement.objects.get_or_create(
                **achievement
            )
            AchievementCat.objects.create(
                achievement=current_achievement,
                cat=cat
            )
        return cat
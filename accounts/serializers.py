from rest_framework import serializers
from accounts.models import MyUser
from django.contrib.auth import get_user_model


class RegisterSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(write_only=True)

    def validate(self, data):
            if data['password'] != data['password2']:
                raise serializers.ValidationError({"error":"Passwords do not match."})
    
            return data
            
    def validate_email(self,value):
            if MyUser.objects.filter(email=value).exists():
                raise serializers.ValidationError("Email already exists.")
    
            return value
            
    def create_user(self, validated_data):
            validated_data.pop("password2")
    
            user = MyUser.objects.create_user(
                **validated_data
            )
            return user 

    def validate_role(self, value):
        if value not in ["customer", "seller"]:
            raise serializers.ValidationError(
                "Invalid role. Choose customer or seller."
            )
        return value

    class Meta:
        model = MyUser
        fields = ['email','username','password','password2','role']
        extra_kwargs = {
            "password": {"write_only": True}
        }

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        try:
            user = MyUser.objects.get(email=data["email"])
        except MyUser.DoesNotExist:
            raise serializers.ValidationError("Invalid email or password.")

        if not user.check_password(data["password"]):
            raise serializers.ValidationError("Invalid email or password.")

        if not user.is_active:
            raise serializers.ValidationError("Account is inactive.")

        data["user"] = user
        return data

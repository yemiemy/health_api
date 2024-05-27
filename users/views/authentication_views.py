from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from users.serializers import TokenSerializer


class TokenLoginView(APIView):
    throttle_classes = ()
    permission_classes = ()
    serializer_class = TokenSerializer

    def get_serializer_context(self):
        return {
            "request": self.request,
            "format": self.format_kwarg,
            "view": self,
        }

    def get_serializer(self, *args, **kwargs):
        kwargs["context"] = self.get_serializer_context()
        return self.serializer_class(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.save()
        return Response(
            {
                "token": data.token.key,
                "is_medical_professional": data.token.user.is_staff,
            },
            status=status.HTTP_200_OK,
        )


class TokenLogoutView(APIView):
    serializer_class = TokenSerializer

    def get_serializer_context(self):
        return {"request": self.request}

    def get_serializer(self, *args, **kwargs):
        kwargs["context"] = self.get_serializer_context()
        return self.serializer_class(*args, **kwargs)

    def delete(self, request, *args, **kwargs):
        serializer = self.get_serializer()
        serializer.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

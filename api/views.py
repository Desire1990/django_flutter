from django.db import connection, transaction, IntegrityError
from django.shortcuts import render
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Sum, Count
from rest_framework import viewsets, generics, mixins
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from django.db import transaction
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from django.http import JsonResponse
from django_filters import rest_framework as filters
from rest_framework.pagination import PageNumberPagination
# third party
from collections import OrderedDict
from rest_framework import viewsets, filters

from .models import *
from .serializers import *

class Pagination(PageNumberPagination):
    page_size = 10
    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('count', self.page.paginator.count),
            ('page', self.page.number),
            ('num_page', self.page.paginator.num_pages),
            ('results', data)
        ]))


class TokenPairView(TokenObtainPairView):
    serializer_class = TokenPairSerializer

class UserViewset(viewsets.ModelViewSet):
    authentication_classes = (SessionAuthentication, JWTAuthentication)
    permission_classes = [IsAuthenticated, IsAdminUser]
    queryset = User.objects.filter()
    pagination_class = Pagination
    serializer_class = UserSerializer
    filter_backends = DjangoFilterBackend,
    filter_fields = {

        "username":["exact"]
    }

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = request.data
        user = User(
            username = data.get("username"),
            email = data.get("email"),
            first_name = data.get("first_name"),
            last_name = data.get("last_name")
        )
        user.set_password("password")

        user.save()
        serializer = UserSerializer(user, many=False)
        return Response(serializer.data, 201)

    def update(self, request, *args, **kwargs):
        user = request.user
        data = request.data
        username = data.get("username")
        if username : user.username = username
        password = data.get("password")
        if password : user.set_password(password)
        user.save()
        serializer = UserSerializer(user, many=False)
        return Response(serializer.data, 201)

    def patch(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        user = self.get_object()
        user.is_active = False
        user.save()
        return Response({'status': 'success'}, 204)


class StudentViewset(viewsets.ModelViewSet):
    authentication_classes = (SessionAuthentication, JWTAuthentication)
    permission_classes = [IsAuthenticated, ]
    queryset = Student.objects.all()
    pagination_class = Pagination
    serializer_class = StudentSerializer
    filter_backends = DjangoFilterBackend,
    filter_fields = {
        "date":["exact"]
    }
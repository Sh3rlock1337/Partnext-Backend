from django.shortcuts import render
from rest_framework import viewsets

from rest_framework.views import APIView
from rest_framework.response import Response

from rest_framework import permissions, status

from permissions.models import Group
from permissions.serializers import GroupSerializer

from permissions.models import Permission
from permissions.serializers import PermissionSerializer


# Create your views here.

class GroupList(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        groups = Group.objects.all()
        serializer = GroupSerializer(groups, many=True)
        return Response(serializer.data)


    def post(self, request):
        serializer = GroupSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PermissionList(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        permissions = Permission.objects.all()
        serializer = PermissionSerializer(permissions, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = PermissionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
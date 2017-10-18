from django.shortcuts import render
from rest_framework.decorators import api_view, APIView
from django.views.decorators.clickjacking import xframe_options_exempt, xframe_options_deny


# Create your views here.
class AppInstall(APIView):
    @xframe_options_exempt
    def get(self, request, format=None):
        result_dict = {}
        return render(request, 'firstapp/app_install.html', result_dict)

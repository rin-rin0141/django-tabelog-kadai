from django.contrib.auth import logout
from django.shortcuts import redirect
from django.views import View


class AdminLogoutView(View):
    
    def post(self, request):
        logout(request)
        return redirect("/admin/login/")
    
    def get(self, request):
        logout(request)
        return redirect("/admin/login/")

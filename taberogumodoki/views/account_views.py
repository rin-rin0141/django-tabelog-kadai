from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.shortcuts import render, redirect
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.contrib.auth import logout
from django.views.generic import CreateView, UpdateView
from django.contrib.auth.views import LoginView
from django.contrib.auth import get_user_model
from taberogumodoki.forms import UserCreationForm


class SignUpView(CreateView):
    form_class = UserCreationForm
    success_url = '/login/'
    template_name = 'pages/login_signup.html'

    def form_valid(self, form):
        messages.success(self.request, '新規登録が完了しました。続けてログインしてください。')
        return super().form_valid(form)


class Login(LoginView):
    template_name = 'pages/login_signup.html'

    def form_valid(self, form):
        messages.success(self.request, 'ログインしました。')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'エラーでログインできません。')
        return super().form_invalid(form)


class AccountUpdateView(LoginRequiredMixin, UpdateView):
    model = get_user_model()
    template_name = 'pages/account.html'
    fields = ('username', 'email',)
    success_url = '/account/'

    def get_object(self):
        # URL Pathからではなく、現在のユーザーから直接pkを取得
        self.kwargs['pk'] = self.request.user.pk
        return super().get_object()


class ProfileView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, "pages/profile.html")

    def post(self, request):
        user = request.user

        # ======================
        # パスワード変更フォームが送られた場合
        # ======================
        if "new_password" in request.POST:
            new_password = request.POST.get("new_password")
            new_password_confirm = request.POST.get("new_password_confirm")

            if new_password != new_password_confirm:
                messages.error(request, "パスワードが一致しません")
                return redirect("profile")

            try:
                validate_password(new_password, user)
            except ValidationError as e:
                for error in e.messages:
                    messages.error(request, error)
                return redirect("profile")

            user.set_password(new_password)
            user.save()

            # 強制ログアウト
            logout(request)
            messages.success(request, "パスワードを変更しました。再ログインしてください。")
            return redirect("login")

        # ======================
        # プロフィール更新（既存処理）
        # ======================
        profile = user.profile
        profile.name = request.POST.get("name")
        profile.zipcode = request.POST.get("zipcode")
        profile.prefecture = request.POST.get("prefecture")
        profile.city = request.POST.get("city")
        profile.address1 = request.POST.get("address1")
        profile.address2 = request.POST.get("address2")
        profile.tel = request.POST.get("tel")
        profile.save()

        messages.success(request, "プロフィールを更新しました")
        return redirect("profile")
from random import random

from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required, permission_required, user_passes_test
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import PermissionRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.contrib.auth.views import LogoutView
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.views import View
from django.views.decorators.cache import cache_page
from django.views.generic import CreateView, DetailView, ListView, UpdateView
from django.urls import reverse, reverse_lazy
from django.utils.translation import gettext_lazy as _, ngettext

from .models import Profile


class HelloView(View):
    welcome_text = _("welcome hello world")

    def get(self, request: HttpRequest) -> HttpResponse:
        items_str = request.GET.get("items") or 0
        items = int(items_str)
        products_line = ngettext(
            "one product",
            "{count} products",
            items,
        )
        products_line = products_line.format(count=items)
        return HttpResponse(
            f"<h1>{self.welcome_text}</h1>"
            f"<p><h2>{products_line}</h2></p>"
        )
    
    
class AboutMeView(DetailView):
    permission_required = "myauth.change_user"
    template_name = "myauth/about-me.html"
    model = Profile

    def get_object(self, queryset=None):
        return Profile.objects.get(user=self.request.user)


class UpdateAvatarView(UserPassesTestMixin, UpdateView):
    def test_func(self):
        return self.request.user.is_superuser or (self.permission_required and self.model.user.pk)

    permission_required = "myauth.change_user"
    template_name = "myauth/update_avatar.html"
    model = Profile
    fields = "avatar",

    def get_success_url(self):
        return reverse(
            "myauth:about-me.html",
            kwargs={"pk": self.object.pk},
        )

    def form_valid(self, form):
        response = super().form_valid(form)

        return response


class UserRegisterView(CreateView):
    form_class = UserCreationForm
    template_name = "myauth/register.html"
    success_url = reverse_lazy("myauth:about-me")

    def form_valid(self, form):
        response = super().form_valid(form)
        Profile.objects.create(user=self.object)
        username = form.cleaned_data.get("username")
        password = form.cleaned_data.get("password1")
        user = authenticate(
            self.request,
            username=username,
            password=password,
        )
        login(request=self.request, user=user)
        return response


class ProfileDetailView(DetailView):
    template_name = "myauth/profile_form.html"
    model = Profile
    context_object_name = "profile"


class ProfileUpdateView(UserPassesTestMixin, PermissionRequiredMixin, UpdateView):
    def test_func(self):
        return self.request.user.is_staff or (self.request.user.id == self.object.user_id)

    permission_required = "myauth.change_user"
    model = Profile
    fields = "bio", "avatar"
    template_name_suffix = "_update_form"

    def get_success_url(self):
        return reverse(
            "myauth:profile_detail",
            kwargs={"pk": self.object.pk},
        )

    def form_valid(self, form):
        response = super().form_valid(form)

        return response


class MyLogoutView(LogoutView):
    next_page = reverse_lazy("myauth:login")


class UsersListView(ListView):
    template_name = 'myauth/profiles-list.html'
    context_object_name = "users"
    queryset = User.objects.filter()


@user_passes_test(lambda u: u.is_superuser)
def set_cookie_view(request: HttpRequest) -> HttpResponse:
    response = HttpResponse("Cookie set")
    response.set_cookie("fizz", "buzz", max_age=3600)
    return response


@cache_page(60)
def get_cookie_view(request: HttpRequest) -> HttpResponse:
    value = request.COOKIES.get("fizz", "default value")
    return HttpResponse(f"Cookie value: {value!r} + {random()}")


@permission_required("myauth.view_profile", raise_exception=True)
def set_session_view(request: HttpRequest) -> HttpResponse:
    request.session["foobar"] = "spameggs"
    return HttpResponse("Session set!")


@login_required
def get_session_view(request: HttpRequest) -> HttpResponse:
    value = request.session.get("foobar", "default")
    return HttpResponse(f"Session value: {value!r}")


class FooBarView(View):
    def get(self, response: HttpResponse) -> JsonResponse:
        return JsonResponse({"foo": "bar", "spam": "eggs"})

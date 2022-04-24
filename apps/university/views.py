from typing import (
    Optional,
    Union,
)

from django.shortcuts import (
    # render,  # Function returns HttpResponse filled of template with context
    redirect,  # Function that returns HttpResponseRedirect by URL name
)
from django.http import (
    HttpResponse,  # HttpResponse class instance
    HttpResponseRedirect,
)
# from django.contrib.auth.models import User
from django.db.models import QuerySet  # QuerySet type
from django.core.handlers.wsgi import WSGIRequest
from django.contrib.auth import (
    login,  # Fill the request.user with data of sent user instance
    logout,  # Errase the current authenticated user's ID from the request
    authenticate,
)
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin

from university.models import (
    Homework,
)
from auths.models import CustomUser  # Imported class CustomUser
from auths.forms import CustomUserForm
from abstracts.handlers import ViewHandler
from abstracts.mixins import HttpResponseMixin
from university.forms import (
    CreateHWForm,
)


class IndexView(ViewHandler, View):  
    def get(self, request: WSGIRequest) -> HttpResponse:  
        response: Optional[HttpResponse] = self.get_validated_response(
            request
        )
        if response:
            return response

        homeworks: QuerySet = Homework.objects.filter(
            user=request.user,
            is_passed=False
        )  # authenticated user's homeworks
        return self.get_http_response(
            request=request,
            template_name='my_new_app/user_main_page.html',
            context={'homeworks': homeworks}
        )


class ShowView(ViewHandler, View):  
    def get(
        self,
        request: WSGIRequest,
        user_id: int
    ) -> HttpResponse:  
        response: Optional[HttpResponse] = self.get_validated_response(
            request=request
        )
        if response:
            return response
        user: CustomUser = CustomUser.objects.get(pk=user_id)
        context: dict = {
            "ctx_title": 'Профиль пользователя',
            "ctx_user": user,
        }
        return self.get_http_response(
            request=request,
            template_name="my_new_app/user_profile.html",
            context=context
        )


class UserRegisterView(HttpResponseMixin, View):  
    def get(
        self,
        request: WSGIRequest
    ) -> Union[HttpResponse, HttpResponseRedirect]:  
        if not request.user.is_authenticated:
            form: CustomUserForm = CustomUserForm(request.POST)
            return self.get_http_response(
                request=request,
                template_name="my_new_app/register_form.html",
                context={"form": form}
            )
        return redirect('page_main')

    def post(
        self,
        request: WSGIRequest
    ) -> HttpResponseRedirect:  
        form: CustomUserForm = CustomUserForm(
            request.POST
        )
        if form.is_valid():
            user: CustomUser = form.save(
                commit=False
            )
            email: str = form.cleaned_data['email']
            password: str = form.cleaned_data['password']
            user.email = email
            user.set_password(password)
            user.save()
            user: CustomUser = authenticate(
                email=email,
                password=password
            )
            if user and user.is_active:
                login(request, user)
        return redirect('register')


class UserLoginView(HttpResponseMixin, View):      
    def get(
        self,
        request: WSGIRequest
    ) -> Union[HttpResponse, HttpResponseRedirect]:  
        if not request.user.is_authenticated:
            form: CustomUserForm = CustomUserForm(request.POST)
            return self.get_http_response(
                request=request,
                template_name="my_new_app/login.html",
                context={"form": form}
            )
        return redirect('page_main')

    def post(
        self,
        request: WSGIRequest
    ) -> Union[HttpResponse, HttpResponseRedirect]:  
        email: str = request.POST['email']
        password: str = request.POST['password']
        user: CustomUser = authenticate(
            email=email,
            password=password
        )
        if not user:
            return self.get_http_response(
                request=request,
                template_name='my_new_app/login.html',
                context={
                    'error_message': 'Неверные данные',
                    "form": CustomUserForm(request.POST)
                }
            )
        if not user.is_active:
            return self.get_http_response(
                request=request,
                template_name='my_new_app/login.html',
                context={
                    'error_message': 'Ваш аккаунт был удалён',
                    "form": CustomUserForm(request.POST)
                }
            )
        login(request, user)
        return redirect('page_main')


class PassedHomeworksView(ViewHandler, View):  
    def get(
        self,
        request: WSGIRequest
    ) -> HttpResponse:  
        response: Optional[HttpResponse] = self.get_validated_response(request)
        if response:
            return response
        passed_homeworks: QuerySet = Homework.objects.filter(
            user=request.user,
            is_passed=True
        )
        return self.get_http_response(
            request=request,
            template_name='my_new_app/user_main_page.html',
            context={'homeworks': passed_homeworks}
        )


class UserLogoutView(LoginRequiredMixin, View):  
    raise_exception = True

    def get(self, request: WSGIRequest) -> HttpResponseRedirect:  
        logout(request)
        return redirect('login')


class CreateHomeworkView(LoginRequiredMixin, HttpResponseMixin, View):  
    raise_exception: bool = True
    form: CreateHWForm = CreateHWForm()
    ALLOWED_IMAGE_FILE_TYPES = {
        'jpeg',
        'png',
        'img',
    }

    def fill_form(
        self,
        request: WSGIRequest
    ) -> None:  
        if request.POST or request.FILES:
            self.form = CreateHWForm(request.POST, request.FILES)

    def get(
        self,
        request: WSGIRequest
    ) -> HttpResponse:  
        self.fill_form(request=request)
        return self.get_http_response(
            request=request,
            template_name='my_new_app/create_homework.html',
            context={"form": self.form}
        )

    def post(
        self,
        request: WSGIRequest
    ) -> Union[HttpResponseRedirect, HttpResponse]:  
        self.fill_form(request=request)
        if self.form.is_valid():
            print('You are validated')
            my_homework: Homework = self.form.save(commit=False)
            my_homework.user = request.user
            logo_type: str = self.form.cleaned_data['logo'].\
                content_type.split('/')[1]
            if logo_type not in self.ALLOWED_IMAGE_FILE_TYPES:
                context: dict = {
                    "form": self.form,
                    'error_message': 'Данный формат картинки недоступен'
                }
                return self.get_http_response(
                    request=request,
                    template_name='my_new_app/create_homework.html',
                    context=context
                )
            my_homework.save()
            return redirect("page_main")
        return redirect("create_hw")
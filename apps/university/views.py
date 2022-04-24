from typing import (
    Optional,
)
from django.db.models import (
    QuerySet,
    Q,
)

from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse
from django.shortcuts import (
    render,
    get_object_or_404,
)
from django.contrib.auth import (
    authenticate as dj_authenticate,
    login as dj_login,
    logout as dj_logout,
)
from django.views import View

from abstracts.handlers import ViewHandler
from auths.forms import CustomUserForm
from auths.models import CustomUser
from university.models import (
    Homework,
    File,
)
from university.forms import (
    HomeworkForm,
    FileForm,
)


class IndexView(ViewHandler, View):
    """Index View."""

    queryset: QuerySet = Homework.objects.get_not_deleted()
    template_name: str = 'university/index.html'

    def get(
        self,
        request: WSGIRequest,
        *args: tuple,
        **kwargs: dict
    ) -> HttpResponse:
        """GET request handler."""

        response: Optional[HttpResponse] = \
            self.get_validated_response(
                request
            )
        if response:
            return response

        homeworks: QuerySet = self.queryset.filter(
            user=request.user
        )
        query: str = request.GET.get(
            'query', ''
        )
        if query:
            homeworks = homeworks.filter(
                Q(title__icontains=query) |
                Q(subject__icontains=query)
            ).distinct()

        if not homeworks:
            homeworks = self.queryset

        return self.get_http_response(
            request,
            template_name=self.template_name,
            context={
                'ctx_title': 'Главная страница',
                'ctx_homeworks': homeworks,
                'ctx_user': request.user,
            }
        )


class ShowView(ViewHandler, View):
    """Show View."""

    queryset: QuerySet = Homework.objects.get_not_deleted()
    template_name: str = 'university/profile.html'

    def get(
        self,
        request: WSGIRequest,
        *args: tuple,
        **kwargs: dict
    ) -> HttpResponse:
        """GET request handler."""

        homework_id: int = kwargs.get(
            'homework_id', 0
        )
        homework: Optional[CustomUser] = None
        try:
            homework = self.queryset.filter(
                user=request.user
            ).get(
                id=homework_id
            )
        except Homework.DoesNotExist:
            return self.get_http_response(
                request,
                'university/index.html'
            )
        else:
            context: dict = {
                'ctx_title': 'Профиль пользователя',
                'ctx_homework': homework,
            }
            return self.get_http_response(
                request,
                self.template_name,
                context
            )


class HomeworkDetailView(ViewHandler, View):
    """Homework Detail View."""

    template_name: str = 'university/homework_detail.html'

    def get(
        self,
        request: WSGIRequest,
        homework_id: int,
        *args: tuple,
        **kwargs: dict
    ) -> HttpResponse:
        """GET request handler."""

        response: Optional[HttpResponse] = \
            self.get_validated_response(
                request
            )
        if response:
            return response

        homework: Homework = get_object_or_404(
            Homework,
            pk=homework_id
        )
        return self.get_http_response(
            request,
            template_name=self.template_name,
            context={
                'ctx_homework': homework,
            }
        )


class HomeworkCreateView(ViewHandler, View):
    """Homework Create View."""

    form: HomeworkForm = HomeworkForm
    template_name: str = 'university/homework_create.html'

    def get(
        self,
        request: WSGIRequest,
        *args: tuple,
        **kwargs: dict
    ) -> HttpResponse:
        """GET request handler."""

        response: Optional[HttpResponse] = \
            self.get_validated_response(
                request
            )
        if response:
            return response

        return self.get_http_response(
            request,
            template_name=self.template_name,
            context={
                'ctx_form': self.form(),
            }
        )

    def post(
        self,
        request: WSGIRequest,
        *args: tuple,
        **kwargs: dict
    ) -> HttpResponse:
        """POST request handler."""

        _form: HomeworkForm = self.form(
            request.POST or None,
            request.FILES or None
        )
        if not _form.is_valid():
            context: dict = {
                'ctx_form': _form,
            }
            return self.get_http_response(
                request,
                self.template_name,
                context
            )
        homework: Homework = _form.save(
            commit=False
        )
        homework.user = request.user
        homework.logo = request.FILES['logo']

        file_type: str = homework.logo.url.split('.')[-1].lower()

        if file_type not in Homework.IMAGE_TYPES:

            context: dict = {
                'ctx_form': _form,
                'ctx_homework': homework,
                'error_message': 'PNG, JPG, JPEG',
            }
            return self.get_http_response(
                request,
                self.template_name,
                context
            )
        homework.save()

        context: dict = {
            'ctx_homework': homework,
        }
        return self.get_http_response(
            request,
            'university/homework_detail.html',
            context
        )


class HomeworkDeleteView(ViewHandler, View):
    """Homework Delete View."""

    template_name: str = 'university/index.html'

    def post(
        self,
        request: WSGIRequest,
        homework_id: int,
        *args: tuple,
        **kwargs: dict
    ) -> HttpResponse:
        """POST request handler."""

        homework = Homework.objects.get(id=homework_id)
        homework.delete()
        homeworks = Homework.objects.filter(user=request.user)

        context: dict = {
            'ctx_homeworks': homeworks,
        }
        return self.get_http_response(
            request,
            self.template_name,
            context
        )


class HomeworkFilesCheckView(ViewHandler, View):
    """Homework Files Check View."""

    def get(
        self,
        request: WSGIRequest,
        file_id: int,
        *args: tuple,
        **kwargs: dict
    ) -> HttpResponse:
        """POST request handler."""

        from django.http import JsonResponse

        file: File = get_object_or_404(
            File, id=file_id
        )
        try:
            if file.is_checked:
                file.is_checked = False
            else:
                file.is_checked = True
            file.save()

        except (KeyError, File.DoesNotExist):
            return JsonResponse(
                {'success': False}
            )
        return JsonResponse(
            {'success': True}
        )


class HomeworkFilesDeleteView(ViewHandler, View):
    """Homework Files Delete View."""

    template_name: str = 'university/homework_detail.html'

    def post(
        self,
        request: WSGIRequest,
        homework_id: int,
        file_id: int,
        *args: tuple,
        **kwargs: dict
    ) -> HttpResponse:
        """POST request handler."""

        homework: Homework = get_object_or_404(
            Homework,
            id=1
        )
        file: File = Homework.objects.get(
            id=file_id
        )
        #file.delete()

        return self.get_http_response(
            request,
            template_name=self.template_name,
            context={
                'ctx_homework': homework
            }
        )


class HomeworkFilesView(ViewHandler, View):
    """Homework Files View."""

    queryset: QuerySet = Homework.objects.get_not_deleted()
    template_name: str = 'university/homework_files.html'

    def get(
        self,
        request: WSGIRequest,
        filter_by: str,
        *args: tuple,
        **kwargs: dict
    ) -> HttpResponse:
        """GET request handler."""

        if not request.user.is_authenticated:
            return self.get_http_response(
                request,
                'university/user_login.html'
            )
        files: list = []
        try:
            file_ids: list = []
            homework: Homework
            for homework in self.queryset.filter(
                user=request.user
            ):
                file: File
                for file in homework.files.get_not_deleted():
                    file_ids.append(file.id)

            files: QuerySet = File.objects.filter(
                id__in=file_ids
            )
            if filter_by == 'checked':
                files = files.filter(
                    is_checked=True
                )
        except Homework.DoesNotExist:
            pass

        context: dict = {
            'ctx_files': files,
            'ctx_filter_by': filter_by,
        }
        return self.get_http_response(
            request,
            self.template_name,
            context
        )


class HomeworkFilesCreateView(ViewHandler, View):
    """Homework Files Create View."""

    queryset: QuerySet = Homework.objects.get_not_deleted()
    form: FileForm = FileForm
    template_name: str = 'university/homework_files_create.html'

    def post(
        self,
        request: WSGIRequest,
        homework_id: int,
        *args: tuple,
        **kwargs: dict
    ) -> HttpResponse:
        """POST request handler."""

        _form: FileForm = self.form(
            request.POST or None,
            request.FILES or None
        )
        homework: Homework = get_object_or_404(
            Homework,
            id=homework_id
        )
        if not _form.is_valid():
            context: dict = {
                'ctx_form': _form,
                'ctx_homework': homework,
            }
            return self.get_http_response(
                request,
                self.template_name,
                context
            )
        files = homework.files.get_not_deleted()
        form_title: str = _form.cleaned_data.get('title')

        file: File
        for file in files:
            if file.title != form_title:
                continue

            context: dict = {
                'ctx_homework': homework,
                'ctx_form': _form,
                'error_message': 'Файл уже добавлен',
            }
            return self.get_http_response(
                request,
                self.template_name,
                context
            )
        file: File = _form.save(
            commit=False
        )
        file.homework = homework
        file.obj = request.FILES['obj']
        file_type: str = file.obj.url.split('.')[-1].lower()

        if file_type not in File.FILE_TYPES:
            context: dict = {
                'ctx_homework': homework,
                'ctx_form': _form,
                'error_message': 'TXT, PDF',
            }
            return self.get_http_response(
                request,
                self.template_name,
                context
            )
        file.save()

        context: dict = {
            'ctx_homework': homework,
        }
        return self.get_http_response(
            request=request,
            template_name='university/homework_detail.html',
            context={
                'ctx_homework': homework,
            }
        )


class LogoutView(ViewHandler, View):
    """Logout View."""

    template_name: str = 'university/user_login.html'

    def post(
        self,
        request: WSGIRequest,
        *args: tuple,
        **kwargs: dict
    ) -> HttpResponse:
        """POST request handler."""

        dj_logout(request)

        form: CustomUserForm = CustomUserForm(
            request.POST
        )
        context: dict = {
            'ctx_form': form,
        }
        return self.get_http_response(
            request,
            self.template_name,
            context
        )


class LoginView(ViewHandler, View):
    """Login View."""

    template_name: str = 'university/user_login.html'

    def get(
        self,
        request: WSGIRequest,
        *args: tuple,
        **kwargs: dict
    ) -> HttpResponse:
        """GET request handler."""

        return self.get_http_response(
            request,
            self.template_name
        )

    def post(
        self,
        request: WSGIRequest,
        *args: tuple,
        **kwargs: dict
    ) -> HttpResponse:
        """POST request handler."""

        email: str = request.POST['username']
        password: str = request.POST['password']

        user: CustomUser = dj_authenticate(
            username=email,
            password=password
        )
        if not user:
            return self.get_http_response(
                request,
                self.template_name,
                {'error_message': 'Неверные данные'}
            )
        if not user.is_active:
            return self.get_http_response(
                request,
                self.template_name,
                {'error_message': 'Ваш аккаунт был удален'}
            )
        dj_login(request, user)

        homeworks: QuerySet = \
            Homework.objects.get_not_deleted().filter(
                user=request.user
            )
        context: dict = {
            'ctx_title': 'Домашние работы',
            'ctx_homeworks': homeworks,
        }
        return self.get_http_response(
            request,
            'university/index.html',
            context
        )


class RegisterView(ViewHandler, View):
    """Register View."""

    template_name: str = 'university/user_register.html'

    def get(
        self,
        request: WSGIRequest,
        *args: tuple,
        **kwargs: dict
    ) -> HttpResponse:
        """GET request handler."""

        return self.get_http_response(
            request,
            self.template_name
        )

    def post(self,
        request: WSGIRequest,
        *args, 
        **kwargs
    ) -> HttpResponse:
        """POST request handler."""

        form: CustomUserForm = CustomUserForm(
            request.POST
        )
        if not form.is_valid():
            return render(
                request,
                self.template_name,
                {'ctx_form': form}
            )
        user: CustomUser = form.save(
            commit=False
        )
        email: str = form.cleaned_data['email']
        password: str = form.cleaned_data['password']
        user.email = email
        user.set_password(password)
        user.save()

        user: CustomUser = dj_authenticate(
            email=email,
            password=password
        )
        if user and user.is_active:

            dj_login(request, user)

            homeworks: QuerySet = Homework.objects.filter(
                user=request.user
            )
            return self.get_http_response(
                request,
                'university/index.html',
                {'ctx_homeworks': homeworks}
            )

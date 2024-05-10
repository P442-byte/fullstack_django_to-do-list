from django.forms import BaseModelForm
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, FormView
from .models import task
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin



# Create your views here.
class TaskList(LoginRequiredMixin, ListView):
    model = task
    context_object_name = "tasks"
    template_name = "todo/task_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["tasks"] = context["tasks"].filter(user=self.request.user)
        context["count"] = context["tasks"].filter(complete=False).count()

        search_inputs = self.request.GET.get("search-area") or ""
        if search_inputs:
            context["tasks"] = context["tasks"].filter(title__icontains=search_inputs)
            context["search_input"] = search_inputs
            
        return context

class TaskDetail(LoginRequiredMixin, DetailView):
    model = task
    context_object_name = "task"
    template_name = "todo/task_detail.html"

class TaskCreate(LoginRequiredMixin, CreateView):
    model = task
    context_object_name = "task"
    template_name = "todo/task_create.html"
    fields = ["title", "description", "complete"]
    success_url = reverse_lazy("task-list")

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(TaskCreate, self).form_valid(form)

class TaskUpdate(LoginRequiredMixin, UpdateView):
    model = task
    context_object_name = "task"
    template_name = "todo/task_update.html"
    fields = ["title", "description", "complete"]
    success_url = reverse_lazy("task-list")

class TaskDelete(LoginRequiredMixin, DeleteView):
    model = task
    context_object_name = "task"
    template_name = "todo/task_delete.html"
    success_url = reverse_lazy("task-list")

class CustomLoginView(LoginView):
    template_name = 'todo/login.html'
    fields = '__all__'
    redirect_authenticated_user = False

    def get_success_url(self):
        return reverse_lazy('task-list')
    
class RegisterPage(FormView):
    template_name = 'todo/register.html'
    form_class = UserCreationForm
    redirect_authenticated_user = True
    success_url = reverse_lazy('task-list')

    def form_valid(self, form):
        user = form.save()
        if user is not None:
            login(self.request, user)

        return super(RegisterPage, self).form_valid(form)
    
    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect('task-list')
        return super(RegisterPage, self).get(*args, **kwargs)
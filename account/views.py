from typing import Any
from django.http import HttpRequest
from django.http.response import HttpResponse as HttpResponse
from django.shortcuts import render, redirect
from django.views import View
from .forms import UserRegistrationForm, UserLoginForm, EditUserForm
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from home.models import Post
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy
from .models import Relation
# Create your views here.

class UserRegisterView(View):
    form_class = UserRegistrationForm
    template_name = 'account/register.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('home:home')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        form =self.form_class()
        return render(request, self.template_name , {'form': form})
    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            User.objects.create_user(cd['username'], cd['email'], cd['password1'])
            messages.success(request, 'you register sucssesfully', 'sucsess')
            return redirect('home:home')
        return render(request, self.template_name , {'form': form})
    
class UserLoginView(View):
    form_class = UserLoginForm
    template_name = 'account/login.html'

    def setup(self, request, *args, **kwargs):
        self.next = request.GET.get('next')
        return super().setup(request, *args, **kwargs)

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('home:home')
        return super().dispatch(request, *args, **kwargs)

    def get(self,request):
        form = self.form_class()
        return render(request, self.template_name , {'form': form})
    def post(self,request):
        form = self.form_class(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(request, username=cd['username'], password=cd['password'])
            if user is not None:
                login(request, user)
                messages.success(request, 'you logged successfully', 'success')
                if self.next:
                    return redirect(self.next)
                return redirect('home:home')
            messages.error(request,'username or password is wrong','warning')
        return render(request, self.template_name , {'form': form}) 

class UserLogoutView(View):
    def get(self,request):
        logout(request)
        messages.success(request, 'you logout successfully', 'success')
        return redirect('home:home')
    
class UserProfileView(LoginRequiredMixin,View):
    def get(self, request, user_id):
        is_following = False
        user = User.objects.get(pk=user_id)
        posts = user.posts.all()
        relation = Relation.objects.filter(from_user=request.user, to_user=user)
        if relation.exists():
            is_following = True
        return render(request, 'account/profile.html', {'user': user , 'posts': posts, 'is_following': is_following} )   

class UserPasswordResetView(auth_views.PasswordResetView):
    template_name = 'account/password_reset_form.html'
    success_url = reverse_lazy('account:password_reset_done')      
    email_template_name = 'account/password_reset_email.html'

class UserPasswordResetDoneView(auth_views.PasswordResetDoneView):
    template_name = 'account/password_reset_done.html'

class UserPasswordResetConfirmView(auth_views.PasswordResetConfirmView):
       template_name = 'account/password_reset_confirm.html'  
       success_url = reverse_lazy('account:password_reset_confirm') 

class UserPasswordResetCompleteView(auth_views.PasswordResetCompleteView):
           template_name = 'account/password_reset_complete.html'

class UserFollowView(LoginRequiredMixin, View):
    def get(self, request, user_id):
      user = User.objects.get(id=user_id) 
      relation = Relation.objects.filter(from_user=request.user, to_user=user)
      if relation.exists():
          messages.error(request, 'you are already follow this user', 'danger')
      else:
          Relation(from_user=request.user, to_user=user).save()
          messages.success(request, 'you follow this user', 'success')  
          return redirect('account:user_profile', user_id)   



class UserUnfollowView(LoginRequiredMixin, View):
    def get(self, request, user_id):   
        user = User.objects.get(id=user_id) 
        relation = Relation.objects.filter(from_user=request.user, to_user=user)
        if relation.exists():   
            relation.delete()
            messages.success(request, 'you unfollow this user', 'success')
        else:
            messages.error(request, 'you arent following this user', 'danger')
        return redirect('account:user_profile', user_id) 

class EditUserView(LoginRequiredMixin, View):
    form_class = EditUserForm

    def get(self, request):
        form = self.form_class(instance=request.user.profile, initial={'email':request.user.email})
        return render(request, 'account/edit_profile.html', {'form':form})
    
    def post(self, request):
        form = self.form_class(request.POST, instance=request.user.profile)
        if form.is_valid():
            form.save()
            request.user.email = form.cleaned_data['email']
            request.user.save()
            messages.success(request, 'edited successfully', 'succsess')
            return redirect('account:user_profile', request.user.id)


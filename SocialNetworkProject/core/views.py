from django.views.generic.edit import CreateView , UpdateView
from django.shortcuts import render , redirect
from django.http import HttpResponse
from .forms import *
from .models import *
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate , login , logout
from django.utils.decorators import method_decorator
from django.views.generic.list import ListView

# Create your views here.
def index(request):
    return HttpResponse("<h1>Is working</h1>")

class SignupView(CreateView):
    model = User
    form_class = SignupForm
    template_name = 'signup.html'
    
    def form_valid(self, form):
        user = form.save()
        login(self.request,user)
        return redirect('profile')
    
    def get(self , *args, **kwargs) :
        if self.request.user.is_authenticated:
            return redirect('profile')  
        return super(SignupView ,self).get(*args,**kwargs)
 

#log in auth page
 
def login_page(request):
    if request.user.is_authenticated:
        return redirect('profile')
    else:
        if request.method == "GET":
            return render(request , 'login.html')
        elif request.method == "POST":
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request,user)
                return redirect('home-page')
            else:
                print("wrong username or password")
                return redirect('login')
    
def logout_user(requset):
    logout(requset)
    return redirect('login')    


@method_decorator(login_required(login_url='login'),name='dispatch')  
class Profile(ListView):
    model = Post
    template_name = "profile.html"
    paginate_by = 5
    
    def get_queryset(self):
        return Post.objects.filter(user=self.request.user).order_by('-date_created')
         
    
    
    

@method_decorator(login_required(login_url='login'),name='dispatch')
class AccountSettingsView(UpdateView):
    model = User
    fields =['first_name','last_name','profile_pic','bio']
    template_name ='account_settings.html'
    success_url ='/profile/'
    
    def get_object(self, queryset = None):
        return self.request.user
    
@method_decorator(login_required(login_url='login'),name='dispatch')    
class CreatePost(CreateView):
    model = Post
    fields =['caption']
    template_name = "new_post.html"
    success_url = '/profile/'
    
    def form_valid(self, form):
        user = self.request.user
        form.instance.user=user
        return super().form_valid(form)
 
    
@method_decorator(login_required(login_url='login'),name='dispatch')  
class FriendProfile(ListView):
    model = Post
    template_name = "friend_profile.html"
    paginate_by = 5
    
    def get(self,request , *args, **kwargs):
        friend_username = self.kwargs['username']
        user_username =self.request.user.username
        if friend_username == user_username :
            return redirect('profile')
        else:
            return super().get(request, *args, **kwargs)
            
          
    def get_context_data(self, *,object_list= None ,**kwargs) :
        context = super().get_context_data(**kwargs)
        friend_username = self.kwargs['username']
        friend = User.objects.get(username = friend_username)
        context['friend'] = friend
        is_following=self.request.user.is_following(friend)
        context['is_following']=is_following
        return context
    
    def get_queryset(self):
        friend_username = self.kwargs['username']
        friend = User.objects.get(username = friend_username)
        return Post.objects.filter(user=friend).order_by('-date_created')    
    
@method_decorator(login_required(login_url='login'),name='dispatch')
class SearchResults(ListView):
    model = User
    template_name = "search_results.html"
    paginate_by = 5
    
    def get_queryset(self):
        search_term = self.request.GET['search-term']
        qs=User.objects.filter(username__contains=search_term)
        return qs
           
            
@login_required(login_url='login')
def follow_user(requset , id):
    user_A=requset.user
    user_B=User.objects.get(id=id)
    new_friend=Friends(user_A=user_A,user_B=user_B)
    new_friend.save()
    return redirect('/user/'+user_B.username)      

@login_required(login_url='login')
def unfollow_user(requset , id):
    user_A=requset.user
    user_B=User.objects.get(id=id)
    Friends.objects.filter(user_A=user_A ,user_B=user_B).delete()
    return redirect('/user/'+user_B.username)      


@method_decorator(login_required(login_url='login'),name='dispatch')
class HomePage(ListView):
    model = Post
    template_name = "home_page.html"
    paginate_by = 5
    
    def get_queryset(self):
        followings = self.request.user.get_followings()
        return Post.objects.filter(user_id__in=followings).order_by('-date_created')
           
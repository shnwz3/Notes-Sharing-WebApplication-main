from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from .models import *
from datetime import date
from django.conf import settings
from .forms import PostForm
from django.contrib import messages
from django.contrib.auth.models import Group
from notes.forms import ContactForm
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.template import Context
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.contrib.auth import authenticate, logout, login

# Create your views here.


def about(request):
    return render(request, 'about.html')


def index(request):
    return render(request, 'index.html')


def contact(request):
    return render(request, 'contact.html')


def userlogin(request):
    error = ""
    if request.method == 'POST':
        u = request.POST['emailid']
        p = request.POST['pwd']
        user = authenticate(username=u, password=p)
        try:
            if user:
                login(request, user)
                error = "no"
            else:
                error = "yes"
        except:
            error = "yes"
    d = {'error': error}
    return render(request, 'login.html', d)


def login_admin(request):
    error = ""
    if request.method == 'POST':
        u = request.POST['uname']
        p = request.POST['pwd']
        user = authenticate(username=u, password=p)
        try:
            if user.is_staff:
                login(request, user)
                error = "no"
            else:
                error = "yes"
        except:
            error = "yes"
    d = {'error': error}
    return render(request, 'login_admin.html', d)


def signup(request):
    error = ""
    if request.method == 'POST':
        f = request.POST['firstname']
        l = request.POST['lastname']
        c = request.POST['contact']
        e = request.POST['emailid']
        p = request.POST['pwd']
        b = request.POST['branch']
        r = request.POST['role']
        # html_content = render_to_string("Email_template.html")
        # subject = "registration"
        # to = e
        # text_content = strip_tags(html_content)
        # email = EmailMultiAlternatives(
        #     subject, text_content, settings.EMAIL_HOST_USER, [to])
        # email.attach_alternative(html_content, "text/html")
        # # email.send()
        user = User.objects.create_user(
            username=e, password=p, first_name=f, last_name=l)
        Signup.objects.create(user=user, contact=c, branch=b, role=r)
        # group=Group.objects.get(name="author")
        # user.groups.add(group)
        error = "no"
    d = {'error': error}
    return render(request, 'signup.html', d)


def admin_home(request):
    if not request.user.is_staff:
        return redirect('login_admin')
    pendnts = Notes.objects.filter(status="pending").count()
    accnts = Notes.objects.filter(status="accept").count()
    rjctnts = Notes.objects.filter(status="reject").count()
    allnts = Notes.objects.all().count()
    d = {'pendnts': pendnts, 'accnts': accnts,
         'rjctnts': rjctnts, 'allnts': allnts}
    return render(request, 'admin_home.html', d)


def Logout(request):
    logout(request)
    return redirect('login')


def user_home(request):
    # redirect ke andar userlogin function ko define karte time (name="") ke andar jo value daali thi na "login" wo daali hai .(login.html file ka reference ni hai ye)
    if not request.user.is_authenticated:
        return redirect('login')
    user = User.objects.get(id=request.user.id)
    data = Signup.objects.get(user=user)
    d = {'data': data, 'user': user}
    return render(request, 'user_home.html', d)


def change_password(request):
    if not request.user.is_authenticated:
        return redirect('login')
    # redirect ke andar userlogin function ko define karte time (name="") ke andar jo value daali thi na "login" wo daali hai .(login.html file ka reference ni hai ye)
    error = ""
    if request.method == "POST":
        o = request.POST['old_pwd']
        n = request.POST['new_pwd']
        c = request.POST['cnfm_pwd']
        if (c == n):
            u = User.objects.get(username__exact=request.user.username)
            u.set_password(n)
            u.save()
            error = "no"
        else:
            error = "yes"
    d = {'error': error}
    return render(request, 'change_password.html', d)


def edit_profile(request):
    # redirect ke andar userlogin function ko define karte time (name="") ke andar jo value daali thi na "login" wo daali hai .(login.html file ka reference ni hai ye)
    if not request.user.is_authenticated:
        return redirect('login')
    user = User.objects.get(id=request.user.id)
    data = Signup.objects.get(user=user)
    error = False
    if request.method == "POST":
        f = request.POST['firstname']
        l = request.POST['lastname']
        c = request.POST['contact']
        b = request.POST['branch']
        user.first_name = f
        user.last_name = l
        data.contact = c
        data.branch = b
        user.save()
        data.save()
        error = True
    d = {'data': data, 'user': user, 'error': error}
    return render(request, 'edit_profile.html', d)


def upload_notes(request):
    if not request.user.is_authenticated:
        return redirect('login')
    error = ""
    if request.method == 'POST':
        b = request.POST['branch']
        s = request.POST['subject']
        n = request.FILES['notesfile']
        f = request.POST['filetype']
        d = request.POST['description']
        crnt_u = User.objects.filter(username=request.user.username).first()
        try:
            Notes.objects.create(user=crnt_u, uploadingdate=date.today(
            ), branch=b, subject=s, notesfile=n, filetype=f, description=d, status='pending')
            error = "no"
        except:
            error = "yes"
    d = {'error': error}
    return render(request, 'upload_notes.html', d)


def view_mynotes(request):
    # redirect ke andar userlogin function ko define karte time (name="") ke andar jo value daali thi na "login" wo daali hai .(login.html file ka reference ni hai ye)
    if not request.user.is_authenticated:
        return redirect('login')
    user = User.objects.get(id=request.user.id)
    notes = Notes.objects.filter(user=user)

    d = {'notes': notes}
    return render(request, 'view_mynotes.html', d)


def delete_mynotes(request, uid):
    # redirect ke andar userlogin function ko define karte time (name="") ke andar jo value daali thi na "login" wo daali hai .(login.html file ka reference ni hai ye)
    if not request.user.is_authenticated:
        return redirect('login')
    notes = Notes.objects.get(id=uid)
    notes.delete()
    return redirect('view_mynotes')


def view_users(request):
    # redirect ke andar userlogin function ko define karte time (name="") ke andar jo value daali thi na "login" wo daali hai .(login.html file ka reference ni hai ye)
    if not request.user.is_authenticated:
        return redirect('login_admin')
    users = Signup.objects.all()
    d = {'users': users}
    return render(request, 'view_users.html', d)


def delete_users(request, uid):
    # redirect ke andar userlogin function ko define karte time (name="") ke andar jo value daali thi na "login" wo daali hai .(login.html file ka reference ni hai ye)
    if not request.user.is_authenticated:
        return redirect('login_admin')
    user = User.objects.get(id=uid)
    user.delete()
    return redirect('view_users')


def pending_notes(request):
    # redirect ke andar userlogin function ko define karte time (name="") ke andar jo value daali thi na "login" wo daali hai .(login.html file ka reference ni hai ye)
    if not request.user.is_authenticated:
        return redirect('login_admin')
    notes = Notes.objects.filter(status="pending")
    d = {'notes': notes}
    return render(request, 'pending_notes.html', d)


def accepted_notes(request):
    # redirect ke andar userlogin function ko define karte time (name="") ke andar jo value daali thi na "login" wo daali hai .(login.html file ka reference ni hai ye)
    if not request.user.is_authenticated:
        return redirect('login_admin')
    notes = Notes.objects.filter(status="accept")
    d = {'notes': notes}
    return render(request, 'accepted_notes.html', d)


def rejected_notes(request):
    # redirect ke andar userlogin function ko define karte time (name="") ke andar jo value daali thi na "login" wo daali hai .(login.html file ka reference ni hai ye)
    if not request.user.is_authenticated:
        return redirect('login_admin')
    notes = Notes.objects.filter(status="reject")
    d = {'notes': notes}
    return render(request, 'rejected_notes.html', d)


def all_notes(request):
    # redirect ke andar userlogin function ko define karte time (name="") ke andar jo value daali thi na "login" wo daali hai .(login.html file ka reference ni hai ye)
    if not request.user.is_authenticated:
        return redirect('login_admin')
    notes = Notes.objects.all()
    d = {'notes': notes}
    return render(request, 'all_notes.html', d)


def view_allnotes(request):
    # redirect ke andar userlogin function ko define karte time (name="") ke andar jo value daali thi na "login" wo daali hai .(login.html file ka reference ni hai ye)
    if not request.user.is_authenticated:
        return redirect('login')
    notes = Notes.objects.all()
    d = {'notes': notes}
    return render(request, 'view_allnotes.html', d)


def assign_status(request, uid):
    # redirect ke andar userlogin function ko define karte time (name="") ke andar jo value daali thi na "login" wo daali hai .(login.html file ka reference ni hai ye)
    if not request.user.is_authenticated:
        return redirect('login_admin')
    notes = Notes.objects.get(id=uid)
    error = ""
    if request.method == 'POST':
        s = request.POST['status']
        try:
            notes.status = s
            notes.save()
            error = "no"
        except:
            error = "yes"
    d = {'notes': notes, 'error': error}
    return render(request, 'assign_status.html', d)


def delete_notes(request, uid):
    # redirect ke andar userlogin function ko define karte time (name="") ke andar jo value daali thi na "login" wo daali hai .(login.html file ka reference ni hai ye)
    if not request.user.is_authenticated:
        return redirect('login')
    notes = Notes.objects.get(id=uid)
    notes.delete()
    return redirect('all_notes')


def home_blog(request):
    if not request.user.is_authenticated:
        return redirect('login')
    posts = Post.objects.all()
    return render(request, 'home_blog.html', {'posts': posts})


def dashboard(request):
    if not request.user.is_authenticated:
        return redirect('login')
    # messages.success(request, "Logged in successfully in your Blog")
    posts = Post.objects.all()
    user = request.user
    full_name = user.get_full_name()
    grps = user.groups.all()
    return render(request, 'dashboard.html', {'posts': posts, 'full_name': full_name, 'groups': grps})


def blog_logout(request):
    logout(request)
    return redirect('index')


def add_post(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            form = PostForm(request.POST)
            if form.is_valid():
                title = form.cleaned_data['title']
                desc = form.cleaned_data['desc']
                pst = Post(title=title, desc=desc)
                messages.success(request, "Post has been added")
                pst.save()
                form = PostForm()
        else:
            form = PostForm()
        return render(request, 'addpost.html', {'form': form})
    else:
        return redirect('login')


def update_post(request, id):
    if request.user.is_authenticated:
        if request.method == 'POST':
            pi = Post.objects.get(pk=id)
            form = PostForm(request.POST, instance=pi)
            if form.is_valid():
                messages.success(request, "You have edited the Post")
                form.save()
        else:
            pi = Post.objects.get(pk=id)
            form = PostForm(instance=pi)
        return render(request, 'updatepost.html', {'form': form})
    else:
        return redirect('login')


def delete_post(request, id):
    if request.user.is_authenticated:
        if request.method == 'POST':
            pi = Post.objects.get(pk=id)
            pi.delete()
        return render(request, 'dashboard.html')
    else:
        return redirect('login')

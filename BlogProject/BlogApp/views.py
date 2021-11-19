from django.shortcuts import render,get_object_or_404
from BlogApp.models import Post
from django.core.paginator import Paginator,PageNotAnInteger,EmptyPage
from django.core.mail import send_mail
from BlogApp.forms import EmailSendForm
from BlogApp.forms import CommentForm
from taggit.models import Tag
# Create your views here.

def post_list_view(request,tag_slug=None):
    post_list=Post.objects.all()

    tag=None
    if tag_slug:
        tag=get_object_or_404(Tag,slug=tag_slug)
        post_list=post_list.filter(tags__in=[tag])

    paginator=Paginator(post_list,2)
    page_number=request.GET.get('page')#not sending any page paramater so here page value is none so that's why error will raise
    #PageNotAnInteger so by default we have to show 1st page post_list=paginator.page(1) and at last page EmptyPage error will raise
    #it will display last page
    try:
        post_list=paginator.page(page_number)
    except PageNotAnInteger:
        post_list=paginator.page(1)
    except EmptyPage:
        post_list=paginator.page(paginator.num_pages)

    return render(request,'BlogApp/post_list.html',{'post_list':post_list})

#from django.views.generic import ListView

#class postlistview(ListView):
 #   model = Post
  #  paginate_by = 3

def post_detail_view(request,year,month,day,post):
    post=get_object_or_404(Post,slug=post,status='published',
                                          publish__year=year,
                                          publish__month=month,
                                          publish__day=day)

    comments = post.comments.filter(active=True)
    csubmit = False
    if request.method == 'POST':
        form = CommentForm(data=request.POST)
        if form.is_valid():
            new_comment = form.save(commit=False)
            new_comment.post = post
            new_comment.save()
            csubmit = True
    else:
        form = CommentForm()
    return render(request,'BlogApp/post_detail.html',{'post':post,'form':form,'csubmit':csubmit,'comments':comments})


def send_mail_view(request,id):
    post=get_object_or_404(Post,id=id,status='published')
    sent=False#by default
    if request.method=='POST':
        form=EmailSendForm(request.POST)
        if form.is_valid():
            cd=form.cleaned_data#this is dictionary and this dictionary conatins end user provided data
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject='{}({}) recommands you to read "{}"'.format(cd['name'],cd['email'],post.title)
            message = 'Read Post At: \n {}\n\n{}\' Comments:\n{}'.format(post_url, cd['name'], cd['comments'])
            send_mail(subject,message,'djangopracticepurpose@gmail.com',[cd['to']])
            sent=True
    else:
        form=EmailSendForm()
    return render(request,'BlogApp/send_mail.html',{'form':form,'post':post,'sent':sent})



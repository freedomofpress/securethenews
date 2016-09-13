from django.shortcuts import render
from django.http import HttpResponse

from scans.models import Site

def index(request):
    sites = Site.objects.all()
    context = { 'sites': sites }
    return render(request, 'sites/index.html', context)

def detail(request, pk):
    site = Site.objects.get(pk=pk)
    context = { 'site': site }
    return render(request, 'sites/detail.html', context)

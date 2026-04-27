from django.shortcuts import render
from .models import RuleSection
def rules_index(request): return render(request,'rules/rules_index.html',{'sections':RuleSection.objects.filter(is_public=True).prefetch_related('items')})

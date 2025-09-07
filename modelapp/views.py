from django.shortcuts import render
from models import Model

# Create your views here.

def model_view(question):

    #Add GPT Algorithm to generate answers in Model.objects.create(answer=answer)
    #Add integrate with admin panel

    return Model.objects.create(question=question)
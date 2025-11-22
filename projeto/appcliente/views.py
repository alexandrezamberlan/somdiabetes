from __future__ import unicode_literals

from django.contrib.staticfiles import finders

from django.conf import settings
from django.contrib import messages
from django.db.models import Q
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.base import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch


from utils.decorators import LoginRequiredMixin, ClienteRequiredMixin


from aviso.models import Aviso
from dado_clinico.models import DadoClinico
from registro_refeicao.models import RegistroRefeicao
from registro_atividade.models import RegistroAtividade
from usuario.models import Usuario

from .forms import ClienteCreateForm, DadoClinicoClienteForm, ClienteRegistroRefeicaoForm
from dado_clinico.forms import BuscaDadoClinicoForm
from registro_atividade.forms import BuscaRegistroAtividadeForm
from registro_refeicao.forms import BuscaRegistroRefeicaoForm



class HomeView(LoginRequiredMixin, ClienteRequiredMixin, TemplateView):
    template_name = 'appcliente/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['avisos'] = Aviso.ativos.filter(destinatario__in=[self.request.user.tipo, 'TODOS'])[0:2]
        return context

class AboutView(LoginRequiredMixin, ClienteRequiredMixin, TemplateView):
    template_name = 'appcliente/about.html'
    

class DadosClienteUpdateView(LoginRequiredMixin, ClienteRequiredMixin, UpdateView):
    model = Usuario
    template_name = 'appcliente/dados_cliente_form.html'
    form_class = ClienteCreateForm  
    
    success_url = 'appcliente_home'

    def get_object(self, queryset=None):
        return self.request.user
     
    def get_success_url(self):
        messages.success(self.request, 'Seus dados clinicos foram alterados com sucesso!')
        return reverse(self.success_url)
    

#Dados Clinicos Cliente Views
class MeusDadosClinicosClienteListView(LoginRequiredMixin, ClienteRequiredMixin, ListView):
    model = DadoClinico
    template_name = 'appcliente/dadoclinico_list.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.GET:
            #quando ja tem dados filtrando
            context['form'] = BuscaDadoClinicoForm(data=self.request.GET)
        else:
            #quando acessa sem dados filtrando
            context['form'] = BuscaDadoClinicoForm()
        return context

    def get_queryset(self):                
        qs = super().get_queryset().filter(cliente=self.request.user)

        if self.request.GET:
            #quando ja tem dados filtrando
            form = BuscaDadoClinicoForm(data=self.request.GET)
        else:
            #quando acessa sem dados filtrando
            form = BuscaDadoClinicoForm()

        if form.is_valid():            
            pesquisa = form.cleaned_data.get('pesquisa')            
                        
            if pesquisa:
                qs = qs.filter(Q(medicamentos__nome_comercial__icontains=pesquisa) | Q(medicamentos__principio_ativo__icontains=pesquisa) | Q(medicamentos__classe_terapeutica__icontains=pesquisa) )
            
        return qs


class MeusDadosClinicosClienteCreateView(LoginRequiredMixin, CreateView):
    model = DadoClinico
    template_name = 'appcliente/dadoclinico_form.html'
    form_class = DadoClinicoClienteForm
    success_url = 'appcliente_dadoclinico_list'
    
    def form_valid(self, form):        
        formulario = form.save(commit=False)
        formulario.cliente = self.request.user
        formulario.save()
        
        return super().form_valid(form)

    def get_success_url(self):
        messages.success(self.request, 'Dado clínico cadastrado com sucesso na plataforma!')
        return reverse(self.success_url)


class MeusDadosClinicosClienteUpdateView(LoginRequiredMixin, UpdateView):
    model = DadoClinico
    template_name = 'appcliente/dadoclinico_form.html'
    form_class = DadoClinicoClienteForm
    success_url = 'appcliente_dadoclinico_list'
    
    def get_success_url(self):
        messages.success(self.request, 'Dado clínico atualizado com sucesso na plataforma!')
        return reverse(self.success_url)


class MeusDadosClinicosClienteDeleteView(LoginRequiredMixin, DeleteView):    
    model = DadoClinico
    template_name = 'appcliente/dadoclinico_confirm_delete.html'
    success_url = 'appcliente_dadoclinico_list'

    def get_success_url(self):
        messages.success(self.request, 'Dado clínico removido com sucesso na plataforma!')
        return reverse(self.success_url) 

    def post(self, request, *args, **kwargs):
        """
        Call the delete() method on the fetched object and then redirect to the
        success URL. If the object is protected, send an error message.
        """
        try:
            self.object = self.get_object()
            self.object.delete()
        except Exception as e:
            messages.error(request, 'Há dependências ligadas à esse Dado Clínico, permissão negada!')
        return redirect(self.success_url)
    
#Refeicao Cliente Views
class MinhaRefeicaoListView(LoginRequiredMixin, ListView):
    model = RegistroRefeicao
    template_name = 'appcliente/registrorefeicao_list.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.GET:
            #quando ja tem dados filtrando
            context['form'] = BuscaRegistroRefeicaoForm(data=self.request.GET)
        else:
            #quando acessa sem dados filtrando
            context['form'] = BuscaRegistroRefeicaoForm()
        return context

    def get_queryset(self):                
        qs = super().get_queryset().filter(cliente__cliente=self.request.user)

        if self.request.GET:
            #quando ja tem dados filtrando
            form = BuscaRegistroRefeicaoForm(data=self.request.GET)
        else:
            #quando acessa sem dados filtrando
            form = BuscaRegistroRefeicaoForm()

        if form.is_valid():            
            pesquisa = form.cleaned_data.get('pesquisa')            
                        
            if pesquisa:
                qs = qs.filter(Q(cliente__cliente__nome__icontains=pesquisa) | Q(registro_alimentacao__icontains=pesquisa))
            
        return qs



class MinhaRefeicaoCreateView(LoginRequiredMixin, CreateView):
    model = RegistroRefeicao
    fields = ['registro_alimentacao', 'glicemia_vigente']
    template_name = 'appcliente/registrorefeicao_form.html'
    success_url = 'appcliente_registrorefeicao_list'

    def form_valid(self, form):
        formulario = form.save(commit=False)
        dado_clinico = DadoClinico.objects.filter(cliente=self.request.user).first()
        formulario.cliente = dado_clinico
        formulario.save()
        return super().form_valid(form)

    def get_success_url(self):
        messages.success(self.request, 'Registro de refeição cadastrado com sucesso na plataforma!')
        return reverse(self.success_url)


# class RegistroRefeicaoUpdateView(LoginRequiredMixin, UpdateView):
#     model = RegistroRefeicao
#     # fields = ['cliente', 'registro_alimentacao', 'glicemia_vigente']
#     form_class = RegistroRefeicaoForm
#     success_url = 'registrorefeicao_list'

#     def get_success_url(self):
#         messages.success(self.request, 'Registro de refeição atualizado com sucesso na plataforma!')
#         return reverse(self.success_url)


class MinhaRefeicaoDeleteView(LoginRequiredMixin, DeleteView):
    model = RegistroRefeicao
    template_name = 'appcliente/registrorefeicao_confirm_delete.html'
    success_url = 'appcliente_registrorefeicao_list'

    def get_success_url(self):
        messages.success(self.request, 'Registro de refeição removido com sucesso na plataforma!')
        return reverse(self.success_url)

    def post(self, request, *args, **kwargs):
        """
        Call the delete() method on the fetched object and then redirect to the
        success URL. If the object is protected, send an error message.
        """
        self.object = self.get_object()
        try:
            self.object.delete()
        except Exception as e:
            messages.error(request, 'Há dependências ligadas à esse Registro de refeição, permissão negada!')
        return redirect(self.get_success_url())



#Registro Atividade Cliente Views
class MeuRegistroAtividadeListView(LoginRequiredMixin, ListView):
    model = RegistroAtividade
    template_name = 'appcliente/registroatividade_list.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.GET:
            #quando ja tem dados filtrando
            context['form'] = BuscaRegistroAtividadeForm(data=self.request.GET)
        else:
            #quando acessa sem dados filtrando
            context['form'] = BuscaRegistroAtividadeForm()
        return context

    def get_queryset(self):                        
        qs = super().get_queryset().filter(cliente=self.request.user)

        if self.request.GET:
            #quando ja tem dados filtrando
            form = BuscaRegistroAtividadeForm(data=self.request.GET)
        else:
            #quando acessa sem dados filtrando
            form = BuscaRegistroAtividadeForm()

        if form.is_valid():            
            pesquisa = form.cleaned_data.get('pesquisa')            
                        
            if pesquisa:
                qs = qs.filter(Q(cliente__nome__icontains=pesquisa) | Q(atividade__nome__icontains=pesquisa))
            
        return qs


class MeuRegistroAtividadeCreateView(LoginRequiredMixin, CreateView):
    model = RegistroAtividade
    fields = ['data', 'hora', 'atividade', 'duracao', 'esforco', 'frequencia_cardiaca_media']
    template_name = 'appcliente/registroatividade_form.html'
    success_url = 'appcliente_registroatividade_list'

    def get_success_url(self):
        messages.success(self.request, 'Registro de atividade cadastrado com sucesso na plataforma!')
        return reverse(self.success_url)
    
    def form_valid(self, form):        
        formulario = form.save(commit=False)
        formulario.cliente = self.request.user
        formulario.save()
        
        return super().form_valid(form)


class MeuRegistroAtividadeUpdateView(LoginRequiredMixin, UpdateView):
    model = RegistroAtividade
    fields = ['data', 'hora', 'atividade', 'duracao', 'esforco', 'frequencia_cardiaca_media']
    template_name = 'appcliente/registroatividade_form.html'
    success_url = 'appcliente_registroatividade_list'

    def get_success_url(self):
        messages.success(self.request, 'Registro de atividade atualizado com sucesso na plataforma!')
        return reverse(self.success_url)


class MeuRegistroAtividadeDeleteView(LoginRequiredMixin, DeleteView):
    model = RegistroAtividade
    success_url = 'appcliente_registroatividade_list'

    def get_success_url(self):
        messages.success(self.request, 'Registro de atividade removido com sucesso na plataforma!')
        return reverse(self.success_url)

    def post(self, request, *args, **kwargs):
        """
        Call the delete() method on the fetched object and then redirect to the
        success URL. If the object is protected, send an error message.
        """
        self.object = self.get_object()
        try:
            self.object.delete()
        except Exception as e:
            messages.error(request, 'Há dependências ligadas à esse Exercício, permissão negada!')
        return redirect(self.get_success_url())
    

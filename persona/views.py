from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import  login_required
from .forms import *
from django.contrib import messages
from tipos.forms import *
from obras_particulares.views import *
from tramite.forms import FormularioIniciarTramite
from documento.forms import FormularioDocumentoSetFactory
from tramite.models import *
from django.core.mail import send_mail

def mostrar_inspector(request):
    return render(request, 'persona/inspector/inspector.html', {})

def mostrar_profesional(request):
    usuario = request.user
    tipos_de_documentos_requeridos = TipoDocumento.get_tipos_documentos_para_momento(TipoDocumento.INICIAR)
    FormularioDocumentoSet = FormularioDocumentoSetFactory(tipos_de_documentos_requeridos)
    documento_set = FormularioDocumentoSet()
    tramite_form = FormularioIniciarTramite()
  
    if request.method == "POST":
        personas = Persona.objects.filter(dni=request.POST["propietario"])
        persona = personas.exists() and personas.first() or None
        documento_set = FormularioDocumentoSet(request.POST, request.FILES)
        propietario_form = FormularioPropietario(request.POST)
        tramite_form = FormularioIniciarTramite(request.POST)
        propietario = propietario_form.obtener_o_crear(persona)

        if propietario is not None and tramite_form.is_valid() and documento_set.is_valid():
            propietario_form = None
            tramite = tramite_form.save(propietario=propietario)
            tramite.save()
            #docs = documento_set.save(commit=False)
            #print(docs)
            #raise "HOla mundo"
            
    else:
        tramite_form = FormularioIniciarTramite(initial={'profesional':'1'})
        documento_set = FormularioDocumentoSet()
        propietario_form = None

    return render(request, 'persona/profesional/profesional.html', {'tramite_form': tramite_form,
                                                                   'propietario_form': propietario_form,
                                                                   'documento_set': documento_set})

def mostrar_jefe_inspector(request):
    return render(request, 'persona/jefe_inspector/jefe_inspector.html')


def mostrar_propietario(request):
    form = FormularioPropietario()
    return render(request, 'persona/propietario/propietario.html',{'form':form})


@login_required(login_url="login")
@grupo_requerido('visador')
def mostrar_visador(request):
    return render(request, 'persona/visador/visador.html')

@login_required(login_url="login")
@grupo_requerido('visador')
def mostrar_visar(request):
    return render(request, 'persona/visador/visar.html')


FORMS_DIRECTOR = {(k.NAME, k.SUBMIT): k for k in [
    FormularioTipoDocumento,
    FormularioUsuarioPersona,  #este formulario no se necesitaria, solo se dan de alta visador, inspector y administrativo
    FormularioTipoObra,
    FormularioTipoDocumento,
    FormularioAdministrativo,
    FormularioInspector,
    FormularioVisador

]}

@login_required(login_url="login")
@grupo_requerido('director')
def mostrar_director(request):
    usuario = request.user
    values = {}
    for form_name, submit_name in FORMS_DIRECTOR:
        KlassForm = FORMS_DIRECTOR[(form_name, submit_name)]
        if request.method == "POST" and submit_name in request.POST:
            _form = KlassForm(request.POST)
            if _form.is_valid():
                _form.save()
                return redirect(usuario.get_view_name())
            else:
                values["submit_name"] = submit_name
            values[form_name] = _form
        else:
            values[form_name] = KlassForm()

    return render(request, 'persona/director/director.html', values)


def alta_persona(request):
    if request.method == "POST":
        form = FormularioPersona(request.POST)
        if form.is_valid():
            persona = form.save()
            persona.save()
    else:
        form = FormularioPersona()
    return render(request, 'persona/alta/alta_persona.html', {'form': form})

@login_required(login_url="login")
@grupo_requerido('administrativo')
def mostrar_administrativo(request):
    contexto = profesional_list(request)
    return render(request, 'persona/administrativo/administrativo.html', contexto)


def crear_usuario(request, pk_persona):
    usuario = request.user
    persona = get_object_or_404(Persona, pk=pk_persona)
    creado, password, usuario_creado = persona.crear_usuario()
    if creado:
        messages.add_message(request, messages.SUCCESS, 'usuario creado.')
        # Mandar correo al  nuevo usuario con su usurio y clave
        print("Mando correo de creado")
        send_mail(
            'Usuario habilitado',
            'Usted ya puede acceder al sistema: Nombre de usuario: '+persona.mail+' password: '+password,
            'infosopunpsjb@gmail.com',
            [persona.mail],
            fail_silently=False,
        )
        print (password)
    else:
        print("Mando correo informando que se cambio algo en su cuenta de usuario")

    return redirect(usuario.get_view_name())


def profesional_list(request):
    personas = Persona.objects.all()
    profesionales = filter(lambda persona: (persona.usuario is None and persona.profesional is not None), personas)
    contexto = {'personas': profesionales}
    return contexto
    
def propietario_list(request):
    propietarios = Propietario.objects.all()
    contexto = {'propietarios': propietario}
    return render(request, 'persona/administrativo/propietario_list.html', contexto)

# es el de tramites iniciados
def tramite_list(request):
    tramites = Tramite.objects.all()
    #tramites = filter(lambda tramite: (tramite.estado is tramite.estado_actual.iniciado), tramites)
    contexto = {'tramites': tramite}
    return render(request, 'persona/administrativo/tramite_list.html', contexto)
    #return contexto

def tramite_corregidos_list(request):
    tramite = Tramite.objects.all()
    contexto = {'tramites': tramite}
    return render(request, 'persona/administrativo/tramite_corregidos_list.html', contexto)
    #return contexto

def solicitud_final_obra_list(request):
    tramite = Tramite.objects.all()
    contexto = {'tramites': tramite}
    return render(request, 'persona/administrativo/solicitud_final_obra_list.html', contexto)
    #return contexto



def consultar_estado_tramite_list():
    tramites = Tramite.objects.all()
    contexto = {'tramites': tramite}
    return render(request, 'persona/profesional/consultar_estado_tramite.html', contexto)
    #return contexto



def aceptar_tramite(request, pk_tramite):
    tramite = get_object_or_404(Tramite, pk=pk_tramite)
    #poner la funcion que cambia de estado al tramite
    return redirect('persona/administrativo/administrativo.html')

def rechazar_tramite(request, pk_tramite):
    tramite = get_object_or_404(Tramite, pk=pk_tramite)
    #poner la funcion que cambia de estado al tramite
    return redirect('persona/administrativo/administrativo.html')

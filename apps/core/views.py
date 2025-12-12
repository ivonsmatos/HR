from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _

@login_required
@require_http_methods(["GET", "POST"])
def lgpd_consent(request):
    """
    Exibe e processa o consentimento LGPD do usuário.
    """
    if request.method == "POST":
        consent = request.POST.get("consent")
        if consent == "on":
            # Em um cenário real, salvaríamos isso no perfil do usuário ou em um modelo específico de Consentimento
            # Por enquanto, usamos a sessão
            request.session['lgpd_consent_given'] = True
            messages.success(request, _("Consentimento registrado com sucesso."))
            return redirect("dashboard") # Redireciona para dashboard ou home
        else:
            messages.error(request, _("É necessário aceitar os termos para continuar."))

    return render(request, "LGPD_CONSENT.html")

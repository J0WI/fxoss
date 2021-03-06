from __future__ import unicode_literals

from django.shortcuts import redirect
from django.utils.http import is_safe_url

from mezzanine.conf import settings
from mezzanine.pages.page_processors import processor_for

from .forms import AgreementForm
from .models import Agreement


@processor_for('download-agreement')
def download_agreement(request, page):
    form = AgreementForm()
    if request.method == "POST":
        form = AgreementForm(request.POST)
        if form.is_valid():
            settings.use_editable()
            if "HTTP_X_FORWARDED_FOR" in request.META:
                parts = request.META["HTTP_X_FORWARDED_FOR"].split(",", 1)
                ip = parts[0]
            else:
                ip = request.META.get('REMOTE_ADDR') or None
            Agreement.objects.create(
                user=request.user,
                ip=ip,
                version=settings.DOWNLOAD_AGREEMENT_VERSION
            )
            redirect_field_name = 'next'
            default_next = '/'
            next_page = request.POST.get(redirect_field_name, request.GET.get(redirect_field_name))
            next_page = next_page or default_next
            if not is_safe_url(url=next_page, host=request.get_host()):
                next_page = default_next
            if 'waiting_download' in request.session:
                request.session['ready_download'] = request.session['waiting_download']
                del request.session['waiting_download']
            return redirect(next_page)
    return {"form": form}

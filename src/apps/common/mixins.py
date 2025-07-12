from django.shortcuts import redirect
from django.urls import reverse


class AnonymousRequiredMixin:
    authenticated_url = 'account:dashboard'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(reverse(self.authenticated_url))
        return super().dispatch(request, *args, **kwargs)

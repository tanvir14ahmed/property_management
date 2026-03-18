from __future__ import annotations

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView

from properties.models import Apartment, ApartmentOccupancy

from .forms import MessageForm
from .models import Conversation, Message
from django.db.models import Q
from django.views.generic import ListView


class ChatListView(LoginRequiredMixin, ListView):
    model = Apartment
    template_name = "chatapp/list.html"
    context_object_name = "apartments"

    def get_queryset(self):
        user = self.request.user
        if user.is_owner:
            # Show all apartments in owner's buildings that have an active tenant
            return Apartment.objects.filter(
                building__owner=user,
                assignments__is_active=True
            ).distinct().select_related("building", "conversation")
        if user.is_tenant:
            # Show apartments where this user is the active tenant
            return Apartment.objects.filter(
                assignments__tenant=user,
                assignments__is_active=True
            ).select_related("building", "conversation")
        return Apartment.objects.none()


from django.utils import timezone

class ChatRoomView(LoginRequiredMixin, TemplateView):
    template_name = "chatapp/room.html"
    form_class = MessageForm

    def dispatch(self, request, *args, **kwargs):
        self.apartment = get_object_or_404(Apartment, pk=kwargs["pk"], is_active=True)
        if not self._user_has_access(request.user):
            messages.error(request, "You cannot access this chat.")
            return redirect("core:dashboard")
        self.conversation, _ = Conversation.objects.get_or_create(apartment=self.apartment)
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        if request.headers.get('HX-Request') and 'poll' in request.GET:
            context = self.get_context_data()
            return render(request, "chatapp/partials/message_list.html", context)
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Mark other sender's messages as read
        self.conversation.messages.filter(
            ~Q(sender=self.request.user), 
            is_read=False
        ).update(is_read=True, read_at=timezone.now())
        
        context["conversation"] = self.conversation
        context["chat_messages"] = self.conversation.messages.select_related("sender")
        context["form"] = self.form_class()
        return context

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            msg = form.save(commit=False)
            msg.sender = request.user
            msg.conversation = self.conversation
            msg.save()
            
            if request.headers.get('HX-Request'):
                return render(request, "chatapp/partials/single_message.html", {"msg": msg})
                
            return redirect("chatapp:apartment_chat", pk=self.kwargs["pk"])
        return self.get(request, *args, **kwargs)

    def _user_has_access(self, user):
        if self.apartment.building.owner == user:
            return True
        return ApartmentOccupancy.objects.filter(
            apartment=self.apartment, tenant=user, is_active=True
        ).exists()

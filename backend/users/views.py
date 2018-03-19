"""Views for users app."""
from rest_framework import viewsets
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from events.serializers import EventSerializer
from users.serializers import UserProfileFullSerializer
from users.models import UserProfile

class UserProfileViewSet(viewsets.ModelViewSet):   # pylint: disable=too-many-ancestors
    """API endpoint that allows users to be viewed or edited."""
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileFullSerializer

    def followed_bodies_events(self, request, pk=None):  # pylint: disable=C0103,W0613
        """Endpoint to return all events followed by a user."""
        user_profile = get_object_or_404(self.queryset, pk=pk)
        event_list = []
        for body in user_profile.followed_bodies.all():
            self.get_events_recursive(event_list, body)

        events = EventSerializer(event_list, many=True)
        return Response({'count':len(events.data), 'data':events.data})

    @classmethod
    def get_events_recursive(cls, events, body):
        """Gets all events from a body recursively."""
        for child_body_relation in body.children.all():
            cls.get_events_recursive(events, child_body_relation.child)
        events.extend(x for x in body.events.all() if x not in events)

    def retrieve_me(self, request):
        """Retrieves the logged-in user's profile."""
        return Response(UserProfileFullSerializer(request.user.profile).data)

    def update_me(self, request):
        """Update the logged-in user's profile."""
        serializer = UserProfileFullSerializer(request.user.profile, data=request.data)
        if not serializer.is_valid():
            return Response({'error': 'validation failed'})
        serializer.save()
        return request.user.profile

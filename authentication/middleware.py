# from django.contrib.sessions.models import Session
# from django.utils.deprecation import MiddlewareMixin
# from django.contrib.auth import get_user_model
# from time import timezone

# User = get_user_model()

# class OneSessionPerUserMiddleware(MiddlewareMixin):
#     def process_request(self, request):
#         if request.user.is_authenticated:
#             # Get the current user's active session key
#             current_session_key = request.session.session_key

#             # Check if the user has any other active session
#             user_sessions = Session.objects.filter(expire_date__gte=timezone.now())
#             for session in user_sessions:
#                 session_data = session.get_decoded()
#                 if session_data.get('_auth_user_id') == str(request.user.id):
#                     if session.session_key != current_session_key:
#                         # Terminate the old session
#                         session.delete()
                        
#             return None
                        


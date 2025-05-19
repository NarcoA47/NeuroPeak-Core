from django.shortcuts import render
from rest_framework import viewsets, permissions
from .models import Course, Assignment, Quiz, QuizAttempt, QuizQuestion
from .serializers import CourseSerializer, AssignmentSerializer, QuizSerializer, QuizQuestionSerializer
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets, permissions, status
from .models import ChatMessage



class IsLecturer(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.user_type == 'LECTURER'

class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsLecturer()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(lecturer=self.request.user)

    @action(detail=True, methods=['get'], permission_classes=[IsLecturer])
    def student_performance(self, request, pk=None):
        course = self.get_object()
        quizzes = course.quizzes.all()
        students = set()
        performance = []

        for quiz in quizzes:
            attempts = QuizAttempt.objects.filter(quiz=quiz)
            for attempt in attempts:
                students.add(attempt.student)
                performance.append({
                    "student": attempt.student.full_name,
                    "quiz": quiz.title,
                    "score": attempt.score
                })

        return Response({
            "students": [s.full_name for s in students],
            "performance": performance
        })

class AssignmentViewSet(viewsets.ModelViewSet):
    queryset = Assignment.objects.all()
    serializer_class = AssignmentSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsLecturer()]
        return [permissions.IsAuthenticated()]

class QuizViewSet(viewsets.ModelViewSet):
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsLecturer()]
        return [permissions.IsAuthenticated()]
    
class ChatBotViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request):
        user_message = request.data.get('message')
        if not user_message:
            return Response({"reply": "Please provide a message."}, status=status.HTTP_400_BAD_REQUEST)
        from transformers import Conversation
        conversation = Conversation(user_message)
        result = chatbot(conversation)
        reply = result.generated_responses[-1] if result.generated_responses else "Sorry, I didn't understand."

        # Save to database
        ChatMessage.objects.create(
            user=request.user,
            user_message=user_message,
            bot_reply=reply
        )

        return Response({"reply": reply})

class QuizQuestionViewSet(viewsets.ModelViewSet):
    queryset = QuizQuestion.objects.all()
    serializer_class = QuizQuestionSerializer

    def get_queryset(self):
        quiz_id = self.kwargs.get('quiz_id')
        if quiz_id:
            return self.queryset.filter(quiz_id=quiz_id)
        return self.queryset

    def perform_create(self, serializer):
        quiz_id = self.kwargs.get('quiz_id')
        serializer.save(quiz_id=quiz_id)
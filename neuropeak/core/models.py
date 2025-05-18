from django.db import models
from users.models import User

class Course(models.Model):
    course_code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    lecturer = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'user_type': User.UserType.LECTURER})
    # marking_key = models.TextField(help_text="Marking key or rubric for the course.")

    def __str__(self):
        return self.name

class Assignment(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='assignments')
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    marking_key = models.TextField(help_text="Marking key or rubric for the assignment.")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Quiz(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='quizzes')
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    marking_key = models.TextField(help_text="Marking key or rubric for the quiz.")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class ChatMessage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    user_message = models.TextField()
    bot_reply = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email}: {self.user_message[:30]}"

class QuizQuestion(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    correct_answer = models.TextField()
    # Add fields for options if needed

class QuizAttempt(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='attempts')
    student = models.ForeignKey('users.User', on_delete=models.CASCADE, limit_choices_to={'user_type': 'STUDENT'})
    score = models.FloatField()
    attempted_at = models.DateTimeField(auto_now_add=True)

class QuizAnswer(models.Model):
    attempt = models.ForeignKey(QuizAttempt, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(QuizQuestion, on_delete=models.CASCADE)
    student_answer = models.TextField()
    is_correct = models.BooleanField()
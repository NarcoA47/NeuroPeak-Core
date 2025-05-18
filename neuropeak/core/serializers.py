from requests import Response
from rest_framework import serializers
from .models import Course, Assignment, Quiz, QuizAttempt, QuizAnswer, QuizQuestion

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = '__all__'

class AssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assignment
        fields = '__all__'

class QuizSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quiz
        fields = '__all__'

    def validate_marking_key(self, value):
        # If using JSONField, value is already a dict; if TextField, parse it
        import json
        if isinstance(value, str):
            try:
                value = json.loads(value)
            except Exception:
                raise serializers.ValidationError("marking_key must be valid JSON.")

        if not isinstance(value, dict):
            raise serializers.ValidationError("marking_key must be a dictionary of question_id: answer.")

        # Example: ensure every question has an answer (customize as needed)
        if not value:
            raise serializers.ValidationError("marking_key cannot be empty.")
        for question_id, answer in value.items():
            if not answer:
                raise serializers.ValidationError(f"Question {question_id} does not have an answer.")
        return value

class QuizAttemptSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuizAttempt
        fields = '__all__'

    def create(self, request, *args, **kwargs):
        quiz_id = request.data['quiz']
        answers = request.data['answers']  # {question_id: answer, ...}
        quiz = Quiz.objects.get(id=quiz_id)
        student = request.user

        attempt = QuizAttempt.objects.create(quiz=quiz, student=student, score=0)
        correct_count = 0
        wrong_answers = []

        for qid, ans in answers.items():
            question = QuizQuestion.objects.get(id=qid)
            is_correct = (ans.strip().lower() == question.correct_answer.strip().lower())
            QuizAnswer.objects.create(attempt=attempt, question=question, student_answer=ans, is_correct=is_correct)
            if is_correct:
                correct_count += 1
            else:
                wrong_answers.append({
                    "question": question.question_text,
                    "your_answer": ans,
                    "correct_answer": question.correct_answer
                })

        attempt.score = correct_count / len(answers)
        attempt.save()

        return Response({
            "score": attempt.score,
            "wrong_answers": wrong_answers
        })
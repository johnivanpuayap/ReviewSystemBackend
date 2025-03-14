from django.db import models

# users/models.py
from django.db import models
from .utils.util import generate_class_code


class User(models.Model):
    # User roles
    TEACHER = 'teacher'
    STUDENT = 'student'
    USER_ROLES = [
        (TEACHER, 'Teacher'),
        (STUDENT, 'Student'),
    ]

    supabase_user_id = models.CharField(max_length=255, unique=True)
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=255, null=True)
    last_name = models.CharField(max_length=255, null=True)
    role = models.CharField(max_length=255, choices=USER_ROLES, default=STUDENT)

    @property
    def full_name(self):
        # Concatenate first_name and last_name with a space in between
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return self.email


class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class UserAbility(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    ability_level = models.FloatField()

    class Meta:
        unique_together = (('user', 'category'),)

    def __str__(self):
        return f"{self.user.email} - {self.category.name} - {self.ability_level}"


class Question(models.Model):
    id = models.CharField(max_length=10, unique=True, primary_key=True)
    question_text = models.CharField()
    image_url = models.CharField(max_length=255, null=True)
    category = models.ForeignKey(Category, related_name='questions', on_delete=models.CASCADE)
    difficulty = models.FloatField(default=0.0)
    discrimination = models.FloatField(default=1.0)
    guessing = models.FloatField(default=0.0)
    choices = models.JSONField()
    correct_answer = models.CharField(max_length=255)

    def __str__(self):
        return self.question_text


class Assessment(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    questions = models.ManyToManyField("Question", related_name="assessments")
    selected_categories = models.ManyToManyField(Category, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


    PREVIOUS_EXAM = 'previous_exam'
    AI_GENERATED = 'ai_generated'
    MIXED = 'mixed'

    QUESTION_SOURCES = [
        (PREVIOUS_EXAM, 'Previous Exam'),
        (AI_GENERATED, 'AI Generated'),
        (MIXED, 'Mixed'),
    ]

    TEACHER_GENERATED = 'teacher_generated'
    SYSTEM_GENERATED = 'system_generated'
    LESSON_GENERATED = 'lesson_generated'

    QUIZ_CATEGORIES = [
        (TEACHER_GENERATED, 'Teacher Generated'),
        (SYSTEM_GENERATED, 'System Generated'),
        (LESSON_GENERATED, 'Lesson Generated'),
    ]

     = models.CharField(
        max_length=50,
        choices=QUIZ_CATEGORIES,
        blank=True,
        null=True,
        help_text="Only applicable for quizzes"
    )

    def __str__(self):
        return f"{self.__class__.__name__} for {self.user.email}"



class AssessmentResult(models.Model):
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE)
    score = models.IntegerField(default=0)
    time_taken = models.IntegerField(default=0)

    def __str__(self):
        return f'{self.assessment.user.full_name} - {self.assessment} - {self.score}'


class Answer(models.Model):
    result = models.ForeignKey(AssessmentResult, related_name='answers', on_delete=models.CASCADE)
    question = models.ForeignKey(Question, related_name='question', on_delete=models.CASCADE)
    time_spent = models.IntegerField(default=0)
    chosen_answer = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f'Answer for {self.question.question_text} by {self.exam_result.assessment.user.email}'


class Class(models.Model):
    name = models.CharField(max_length=255)
    teacher = models.ForeignKey('User', on_delete=models.CASCADE, limit_choices_to={'role': 'teacher'})
    students = models.ManyToManyField('User', related_name='enrolled_classes', limit_choices_to={'role': 'student'})
    class_code = models.CharField(max_length=8, unique=True, blank=True, editable=False)

    def save(self, *args, **kwargs):
        if not self.class_code:
            self.class_code = generate_class_code()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Lesson(models.Model):
    lesson_name = models.CharField(max_length=255)

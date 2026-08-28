from django.db import models


class University(models.Model):
    name = models.CharField(max_length=255, unique=True)
    short_name = models.CharField(max_length=30, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class AcademicUnit(models.Model):
    university = models.ForeignKey(University, on_delete=models.CASCADE, related_name="academic_units")
    code = models.CharField(max_length=30)
    short_name = models.CharField(max_length=100)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["code"]
        constraints = [models.UniqueConstraint(fields=["university", "code"], name="unique_unit_code_per_university")]
        indexes = [models.Index(fields=["university", "is_active"])]

    def __str__(self) -> str:
        return f"{self.code} - {self.name}"


class Campus(models.Model):
    academic_unit = models.ForeignKey(
        AcademicUnit, on_delete=models.CASCADE, related_name="campuses"
    )
    code = models.CharField(max_length=30)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["code"]
        constraints = [
            models.UniqueConstraint(
                fields=["academic_unit", "code"],
                name="unique_campus_code_per_academic_unit",
            )
        ]
        indexes = [models.Index(fields=["academic_unit", "is_active"])]

    def __str__(self) -> str:
        return f"{self.code} - {self.name}"


class Career(models.Model):
    academic_unit = models.ForeignKey(
        AcademicUnit, on_delete=models.CASCADE, related_name="careers"
    )
    campuses = models.ManyToManyField(
        Campus, related_name="careers", blank=True
    )
    code = models.CharField(max_length=30)
    short_name = models.CharField(max_length=100)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["code"]
        constraints = [
            models.UniqueConstraint(
                fields=["academic_unit", "code"],
                name="unique_career_code_per_academic_unit",
            )
        ]
        indexes = [models.Index(fields=["academic_unit", "is_active"])]

    def __str__(self) -> str:
        return f"{self.code} - {self.name}"


class StudyPlan(models.Model):
    career = models.ForeignKey(
        Career, on_delete=models.CASCADE, related_name="study_plans"
    )
    code = models.CharField(max_length=30)
    title = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_current = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["code"]
        constraints = [
            models.UniqueConstraint(
                fields=["career", "code"],
                name="unique_plan_code_per_career",
            )
        ]
        indexes = [models.Index(fields=["career", "is_active"])]

    def __str__(self) -> str:
        return f"{self.code} - {self.title}"


class StudyArea(models.Model):
    study_plan = models.ForeignKey(
        StudyPlan, on_delete=models.CASCADE, related_name="areas"
    )
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        indexes = [models.Index(fields=["study_plan", "is_active"])]

    def __str__(self) -> str:
        return self.name

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
    intermediate_title = models.CharField(max_length=255, blank=True)
    duration_years = models.PositiveSmallIntegerField(default=5)
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
        constraints = [
            models.UniqueConstraint(
                fields=["study_plan", "name"],
                name="unique_area_name_per_plan",
            )
        ]
        indexes = [models.Index(fields=["study_plan", "is_active"])]

    def __str__(self) -> str:
        return self.name


class Subject(models.Model):
    class Period(models.TextChoices):
        FIRST_QUARTER = "1Q", "1er Cuatrimestre"
        SECOND_QUARTER = "2Q", "2do Cuatrimestre"
        FIRST_BIMESTER = "1B", "1er Bimestre"
        SECOND_BIMESTER = "2B", "2do Bimestre"
        THIRD_BIMESTER = "3B", "3er Bimestre"
        FOURTH_BIMESTER = "4B", "4to Bimestre"
        ANNUAL = "AN", "Anual"

    study_area = models.ForeignKey(
        StudyArea, on_delete=models.CASCADE, related_name="subjects"
    )
    nomenclador = models.ForeignKey(
        "Nomenclador",
        on_delete=models.PROTECT,
        related_name="subjects",
        null=True,
        blank=True,
    )
    nomenclador_extra = models.CharField(max_length=255, blank=True)
    code = models.CharField(max_length=30, unique=True)
    name = models.CharField(max_length=255)
    year = models.PositiveSmallIntegerField()
    period = models.CharField(max_length=2, choices=Period.choices)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["code"]
        indexes = [models.Index(fields=["study_area", "is_active"])]

    def __str__(self) -> str:
        return f"{self.code} - {self.name}"


class Equivalence(models.Model):
    """Equivalencia entre materias de planes distintos (genérica N:M).

    new_subjects: materias del plan más reciente (se muestran primero).
    old_subjects: materias de planes anteriores.
    rule_text: regla de certificación (ej. "Certifica Inglés") para los
        casos que no son materia↔materia; puede acompañar a los lados
        o ir sola.
    """

    new_subjects = models.ManyToManyField(
        Subject, related_name="equivalences_as_new", blank=True
    )
    old_subjects = models.ManyToManyField(
        Subject, related_name="equivalences_as_old", blank=True
    )
    rule_text = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["id"]

    def __str__(self) -> str:
        new_codes = "+".join(
            self.new_subjects.order_by("code").values_list("code", flat=True)
        )
        old_codes = "+".join(
            self.old_subjects.order_by("code").values_list("code", flat=True)
        )
        base = f"{new_codes} ↔ {old_codes}".strip(" ↔")
        if self.rule_text:
            return f"{base} ({self.rule_text})" if base else self.rule_text
        return base or f"Equivalencia #{self.pk}"


class Nomenclador(models.Model):
    discipline = models.CharField(max_length=120)
    subdiscipline = models.CharField(max_length=120)
    specialty = models.CharField(max_length=160)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["discipline", "subdiscipline", "specialty"]
        constraints = [
            models.UniqueConstraint(
                fields=["discipline", "subdiscipline", "specialty"],
                name="unique_nomenclador_combo",
            )
        ]

    def __str__(self) -> str:
        return f"{self.discipline} / {self.subdiscipline} / {self.specialty}"

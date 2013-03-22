from django.contrib import admin

from .models import (Subject, Goal, GoalRecord, Enrollment, Experiment,
                     ExperimentReport, Variant)


class SubjectAdmin(admin.ModelAdmin):

    list_display = (
        '__unicode__', 'registered_as', 'is_registered_user', 'created')
    list_filter = ('created',)
    date_hierarchy = 'created'


admin.site.register(Subject, SubjectAdmin)


class GoalAdmin(admin.ModelAdmin):
    list_display = ("name", "created")
    list_filter = ('created',)
    date_hierarchy = 'created'


admin.site.register(Goal, GoalAdmin)


class GoalRecordAdmin(admin.ModelAdmin):
    list_display = ("goal", "subject", "created", "req_HTTP_REFERER")
    list_filter = ('goal', 'created')
    date_hierarchy = 'created'


admin.site.register(GoalRecord, GoalRecordAdmin)


class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ("subject", "experiment", "variant", "created")
    list_filter = ('experiment', 'variant', 'created')
    date_hierarchy = 'created'


admin.site.register(Enrollment, EnrollmentAdmin)


class ExperimentAdmin(admin.ModelAdmin):
    list_display = ("name", "variants_commasep", "created")
    list_filter = ('created',)
    date_hierarchy = 'created'


admin.site.register(Experiment, ExperimentAdmin)


class ExperimentReportAdmin(admin.ModelAdmin):
    list_display = ("title", "experiment")
    list_filter = ('experiment',)


admin.site.register(ExperimentReport, ExperimentReportAdmin)


class VariantAdmin(admin.ModelAdmin):
    list_display = ("name", "experiment",
                    # "weight"
    )
    list_filter = ('experiment',)


admin.site.register(Variant, VariantAdmin)

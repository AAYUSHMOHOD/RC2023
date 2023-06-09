from django.contrib import admin

from .models import *

# Register Models
admin.site.register(Profile)
admin.site.register(User_Response)
admin.site.register(chatGPTLifeLine)
admin.site.register(Question)
admin.site.register(EasyQuestion)

'''
from import_export.admin import ImportExportModelAdmin
@admin.register(Question)
class QuestionResource(ImportExportModelAdmin):
    class Meta:
        model = Question
        fields = ('question_no','question','answer','is_junior')

@admin.register(EasyQuestion)
class EasyQuestionResource(ImportExportModelAdmin):
    class Meta:
        model = EasyQuestion
        fields = ('easyquestion_no','easyquestion','easyanswer')
'''
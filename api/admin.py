from django.contrib import admin
from . import models


admin.site.register(models.CustomUser)
admin.site.register(models.OTP)
admin.site.register(models.Role)
admin.site.register(models.University)
admin.site.register(models.Faculty)
admin.site.register(models.Department)
admin.site.register(models.Course)
admin.site.register(models.StudentRecord)
admin.site.register(models.Document)
admin.site.register(models.ServiceRequest)
admin.site.register(models.RequestStatus)
admin.site.register(models.Gender)
admin.site.register(models.EmailLink)
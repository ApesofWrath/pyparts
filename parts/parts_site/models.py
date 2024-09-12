from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _
from storages.backends.gcloud import GoogleCloudStorage

#PART MANAGEMENT MODELS

class PartStatus(models.IntegerChoices):
    NEW = 1, _("New Part")
    IN_DESIGN = 2, _("In Design")
    IN_DESGIN_REVIEW = 3, _("In Design Review")
    DESIGN_REVIEWED = 4, _("Design Review Complete")
    MFG_REVIEWED = 5, _("Manufacturing Review Complete")
    IN_MANUFACTURE = 6, _("In Manufacturing")
    MANUFACTURED = 7, _("Manufacturing Complete")
    QUALITY_CHECKED = 8, _("Quality Check Complete")
    IN_ASSEMBLY = 9, _("In Assembly")
    ASSEMBLED = 10, _("Assembly Completed")

class MfgTypes(models.TextChoices):
    CNC_MILL = "CNC_MILL", _("CNC Mill")
    MANUAL_MILL = "MANUAL_MILL", _("Manual Mill")
    ROUTER = "ROUTER", _("Router")
    LATHE = "LATHE", _("Lathe")
    THREE_D_PRINT = "3D_PRINT", _("3D Printer")
    LASER_CUT = "LASER_CUT", _("Laser Cutter")

class Project(models.Model):
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=200)
    prefix = models.CharField(max_length=10)

    def __str__(self):
        return self.name

class Assembly(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    part_number = models.CharField(max_length=200)
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=200)
    status = models.PositiveSmallIntegerField(choices=PartStatus, default=PartStatus.NEW)
    
    def __str__(self):
        return self.name
    
class SubAssembly(Assembly):
    assembly = models.ForeignKey(Assembly, related_name="sub", on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class Part(models.Model):
    assembly = models.ForeignKey(Assembly, on_delete=models.CASCADE)
    part_number = models.CharField(max_length=200)
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=200)
    status = models.PositiveSmallIntegerField(choices=PartStatus, default=PartStatus.NEW)
    drawing = models.FileField(upload_to=("uploads/%Y/%m/%d"), storage=GoogleCloudStorage(), null=True, blank=True)
    material = models.CharField(max_length=200, null=True, blank=True)
    quantity = models.IntegerField(null=True, blank=True)
    mfg_type = models.CharField(max_length=200, choices=MfgTypes, null=True, blank=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.name

@receiver(post_save,sender=Part)
def update_assembly_status(sender, instance, **kwargs):
    assembly = instance.assembly
    final_status = PartStatus.NEW
    for status in PartStatus.values:
        count = 0
        for part in assembly.part_set.all():
            if part.status < status:
                break
            count = count + 1
        for sub in assembly.sub.all():
            if sub.status < status:
                break
            count = count + 1
        if count == assembly.part_set.all().count() + assembly.sub.all().count():
            final_status = status
    assembly.status = final_status
    assembly.save()

#ORDER MANAGEMENT MODELS

class OrderStatus(models.IntegerChoices):
    NEW = 1, _("New Order")
    READY = 2, _("Ready to Order")
    PLACED = 3, _("Order Placed")
    RECEIVED = 4, _("Order Received")

class Order(models.Model):
    vendor = models.CharField(max_length=200)
    order_id = models.CharField(max_length=200, null=True, blank=True)
    order_placed_date = models.DateField(null=True, blank=True, verbose_name="Order Placed Date")
    order_recv_date = models.DateField(null=True, blank=True, verbose_name="Order Received Date")
    tracking = models.CharField(max_length=200, null=True, blank=True)
    order_total = models.FloatField(null=True, blank=True)
    status = models.PositiveSmallIntegerField(choices=OrderStatus, default=OrderStatus.NEW)

    def __str__(self):
        return self.order_id
    
class Item(models.Model):
    name = models.CharField(max_length=200)
    vendor = models.CharField(max_length=200)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    part_number = models.CharField(max_length=200)
    unit_price = models.FloatField()
    justification = models.CharField(max_length=200)
    quantity = models.IntegerField()
    link = models.URLField(null=True, blank=True)
    requested_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,)

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        items = self.order.item_set.all()
        total = self.unit_price * self.quantity
        for item in items:
            total = total + (item.unit_price * item.quantity)
        self.order.order_total = total
        self.order.save()
        return super().save(*args, **kwargs)

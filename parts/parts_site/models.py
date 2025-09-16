from django.conf import settings
from django.db import models
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _
import logging

from django_slack import slack_message

logger = logging.getLogger(__name__)

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
    latest_revision = models.ForeignKey('PartRevision', on_delete=models.SET_NULL, null=True, blank=True, related_name='part_latest')

    def __str__(self):
        return self.name

class PartRevision(models.Model):
    part = models.ForeignKey(Part, on_delete=models.CASCADE, related_name='revisions')
    revision_number = models.CharField(max_length=10, default='A')
    status = models.PositiveSmallIntegerField(choices=PartStatus, default=PartStatus.NEW)
    drawing = models.FileField(upload_to="uploads/%Y/%m/%d", null=True, blank=True)
    material = models.CharField(max_length=200, null=True, blank=True)
    quantity = models.IntegerField(null=True, blank=True)
    mfg_type = models.CharField(max_length=200, choices=MfgTypes, null=True, blank=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    notes = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ['-revision_number']
        unique_together = ['part', 'revision_number']

    def __str__(self):
        return f"{self.part.name} - Rev {self.revision_number}"


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
    
@receiver(pre_save, sender=Order)
def send_slack_message_on_ready(sender, instance, **kwargs):
    # Check if this is an existing order (has a primary key) and its status is being updated to READY
    if instance.pk is not None:
        old_instance = Order.objects.get(pk=instance.pk)
        if old_instance.status != OrderStatus.READY and instance.status == OrderStatus.READY:
            attachments = [
                {
                'title': f'{instance.vendor} order is ready to order',
                'fields': [
                    {
                        'title': 'Order Total',
                        'value': f'${instance.order_total}',
                        'short': False
                    },
                    {
                        'title': 'Link to Order',
                        'value': f'<https://parts.team668.org/orders/{instance.pk}/>',
                        'short': False
                    },
                ]
                },
            ]
            try:
                slack_message('slack/order_ready.slack', {
                    'order': instance,
                }, attachments=attachments)
            except Exception as e:
                logger.error(f"Failed to send Slack message for order ready: {e}")
        if old_instance.status != OrderStatus.PLACED and instance.status == OrderStatus.PLACED:
            attachments = [
                {
                'title': f'{instance.vendor} order is placed',
                'fields': [
                    {
                        'title': 'Order Total',
                        'value': f'${instance.order_total}',
                        'short': False
                    },
                    {
                        'title': 'Link to Order',
                        'value': f'<https://parts.team668.org/orders/{instance.pk}/>',
                        'short': False
                    },
                ]
                },
            ]
            try:
                slack_message('slack/order_ready.slack', {
                    'order': instance,
                }, attachments=attachments)
            except Exception as e:
                logger.error(f"Failed to send Slack message for order placed: {e}")
    
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


# Signal definitions
def update_assembly_status(sender, instance, **kwargs):
    assembly = instance.part.assembly
    final_status = PartStatus.NEW
    
    # Check each status level from highest to lowest
    for status in reversed(PartStatus.values):
        all_parts_at_status = True
        
        # Check all parts in this assembly
        for part in assembly.part_set.all():
            if not part.latest_revision or part.latest_revision.status < status:
                all_parts_at_status = False
                break
        
        # Check all sub-assemblies
        if all_parts_at_status:
            for sub in assembly.sub.all():
                if sub.status < status:
                    all_parts_at_status = False
                    break
        
        # If all parts and sub-assemblies are at this status or higher, this is our final status
        if all_parts_at_status:
            final_status = status
            break
    
    assembly.status = final_status
    assembly.save()


@receiver(post_save, sender=PartRevision, dispatch_uid="update_part_latest_revision")
def update_part_latest_revision(sender, instance, **kwargs):
    # Update the part's latest_revision to point to the highest revision letter
    part = instance.part
    # Get the revision with the highest revision_number (latest letter)
    latest_revision = part.revisions.order_by('-revision_number').first()
    if latest_revision:
        part.latest_revision = latest_revision
        part.save()
        
        # Now update the assembly status since the part's latest_revision is updated
        update_assembly_status(sender, instance, **kwargs)

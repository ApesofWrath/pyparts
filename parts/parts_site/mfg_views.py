from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.db.models import F
from django.contrib.auth.decorators import login_required

from .models import *
from .forms import *
from .constants import *

@login_required
def mfg(request):
    project_list = Project.objects.order_by("id")
    context = {"project_list": project_list}
    return render(request, "mfg.html", context)

@login_required
def mfg_project(request, project_id):
    current_project = get_object_or_404(Project, pk=project_id)
    context = {"project": current_project,}
    return render(request, "mfg_project.html", context)

@login_required
def mfg_filters(request, project_id, filter):
    current_project = get_object_or_404(Project, pk=project_id)
    
    assembly_list = []
    for a in current_project.assembly_set.all():
        assembly_list.append(a)
        for a_ in a.sub.all():
            assembly_list.append(a_)
    for a in assembly_list:
        if type(a) == SubAssembly:
            for i in range(len(assembly_list)):
                if assembly_list[i].part_number == a.part_number and type(assembly_list[i]) == Assembly:
                    assembly_list.pop(i)
                    break

    parts_list = None
    for assembly in assembly_list:
        match filter:
            case "todo":
                assembly_f = assembly.part_set.all().filter(status__lte = PartStatus.QUALITY_CHECKED.value)
            case "complete":
                assembly_f = assembly.part_set.all().filter(status__gt = PartStatus.QUALITY_CHECKED.value)
            case _:
                assembly_f = assembly.part_set.all().filter(mfg_type__exact = filter)
        if parts_list:
            parts_list = parts_list.union(parts_list, assembly_f)
        else:
            parts_list = assembly_f

    parts_list = parts_list.order_by(F("status").desc())

    context = {"project": current_project,
               "mfg_types": MfgTypes.choices,
               "parts_list": parts_list,
               "current_filter": filter,
               }

    return render(request, "mfg_filter.html", context)
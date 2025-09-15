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

    parts_list = []
    for assembly in assembly_list:
        parts = assembly.part_set.all()
        for part in parts:
            if part.latest_revision:
                # Add revision info to each part
                part.current_status = part.latest_revision.status
                part.current_status_display = part.latest_revision.get_status_display()
                part.current_mfg_type = part.latest_revision.mfg_type
                part.current_mfg_type_display = part.latest_revision.get_mfg_type_display()
                
                # Apply filters based on latest revision
                should_include = False
                match filter:
                    case "todo":
                        should_include = part.latest_revision.status <= PartStatus.QUALITY_CHECKED.value
                    case "complete":
                        should_include = part.latest_revision.status > PartStatus.QUALITY_CHECKED.value
                    case _:
                        should_include = part.latest_revision.mfg_type == filter
                
                if should_include:
                    parts_list.append(part)
    
    # Sort by status (descending)
    parts_list.sort(key=lambda x: x.current_status if x.current_status else 0, reverse=True)

    context = {"project": current_project,
               "mfg_types": MfgTypes.choices,
               "parts_list": parts_list,
               "current_filter": filter,
               }

    return render(request, "mfg_filter.html", context)
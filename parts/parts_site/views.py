from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from .models import *
from .forms import *
from .constants import *

# Create your views here.

@login_required
def index(request):
    return render(request, "index.html")

@login_required
def projects(request):
    project_list = Project.objects.order_by("id")
    context = {"project_list": project_list}
    return render(request, "projects.html", context)

@login_required
def delete(request, project_id = None, assembly_id = None, part_id = None):
    if part_id:
        part = get_object_or_404(Part, pk=part_id)
        part.delete(keep_parents=True)
        return HttpResponseRedirect(reverse("assembly",args=(project_id, assembly_id,)))
    elif assembly_id:
        assembly = get_object_or_404(Assembly, pk=assembly_id)
        assembly.delete(keep_parents=True)
        return HttpResponseRedirect(reverse("project",args=(project_id,)))
    elif project_id:
        project = get_object_or_404(Project, pk=project_id)
        project.delete(keep_parents=True)
        return HttpResponseRedirect(reverse("projects"))
    
@login_required
def edit(request, project_id = None, assembly_id = None, part_id = None):
    context ={}
 
    if request.method == "POST":
        if part_id:
            form = PartFormEdit(request.POST, request.FILES, user=request.user, instance=get_object_or_404(Part, pk=part_id,))
            print(request.FILES)
        elif assembly_id:
            form = AssemblyFormEdit(request.POST, instance=get_object_or_404(Assembly, pk=assembly_id))
        elif project_id:
            form = ProjectForm(request.POST, instance=get_object_or_404(Project, pk=project_id))
        
        # check if form data is valid
        if form.is_valid():
            # save the form data to model
            form.save()

            if part_id:
                return HttpResponseRedirect(reverse("assembly",args=(project_id, assembly_id,)))
            elif assembly_id:
                return HttpResponseRedirect(reverse("project",args=(project_id,)))
            elif project_id:
                return HttpResponseRedirect(reverse("projects"))
            
    else:
        if part_id:
            form = PartFormEdit(user=request.user, instance=get_object_or_404(Part, pk=part_id))
        elif assembly_id:
            form = AssemblyFormEdit(instance=get_object_or_404(Assembly, pk=assembly_id))
        elif project_id:
            form = ProjectForm(instance=get_object_or_404(Project, pk=project_id))
        
    context['form'] = form
    return render(request, "editobject.html", context)

@login_required    
def newproject(request):
    context ={}
 
    if request.method == "POST":
        form = ProjectForm(request.POST)
        
        # check if form data is valid
        if form.is_valid():
            # save the form data to model
            project = form.save()

            tla_form = AssemblyForm()
            tla = tla_form.save(commit=False)
            tla.name = "Top Level Assembly"
            tla.description = project.name
            tla.project = project
            tla.part_number = f"{TEAM}-{project.prefix}-A-0000"
            tla.status = PartStatus.NEW

            tla.save()

            return HttpResponseRedirect(reverse("project",args=(project.id,)))
    else:
        form = ProjectForm()
        
    context['form']= form
    return render(request, "newobject.html", context)

@login_required
def newassembly(request, project_id, assembly_id = None):
    context ={}
 
    if request.method == "POST":
        if assembly_id:
            form = SubAssemblyForm(request.POST)
        else:
            form = AssemblyForm(request.POST)
        
        # check if form data is valid
        if form.is_valid():
            # save the form data to model
            assembly = form.save(commit=False)
            print(type(assembly))
            current_project = get_object_or_404(Project, pk=project_id)
            assembly.project = current_project
            if(assembly_id):
                current_assembly = get_object_or_404(Assembly, pk=assembly_id)
                assembly.assembly = current_assembly
            assembly_number = 0
            for a in current_project.assembly_set.all():
                if a.part_number.split("-")[2] == "A":
                    if int(a.part_number.split("-")[3]) > assembly_number:
                        assembly_number = int(a.part_number.split("-")[3])
            assembly.part_number = f"{TEAM}-{current_project.prefix}-A-{str(assembly_number+ASM_INCR).zfill(PART_DIGITS)}"
            assembly.status = PartStatus.NEW
            assembly.save()
            form.save_m2m()
            return HttpResponseRedirect(reverse("project",args=(project_id,)))

    else:
        if assembly_id:
            form = SubAssemblyForm()
        else:
            form = AssemblyForm()
        
    context['form']= form
    return render(request, "newobject.html", context)

@login_required
def newpart(request, project_id, assembly_id = None):
    context ={}
 
    if request.method == "POST":
        form = PartForm(request.POST, request.FILES)
        
        # check if form data is valid
        if form.is_valid():
            # save the form data to model
            part = form.save(commit=False)
            current_project = get_object_or_404(Project, pk=project_id)
            current_assembly = part.assembly
            part_number = int(current_assembly.part_number.split("-")[3])
            for p in current_assembly.part_set.all():
                if p.part_number.split("-")[2] == "P":
                    if int(p.part_number.split("-")[3]) > part_number:
                        part_number = int(p.part_number.split("-")[3])
            part.part_number = f"{TEAM}-{current_project.prefix}-P-{str(part_number+1).zfill(PART_DIGITS)}"
            part.status = PartStatus.NEW
            part.save()
            form.save_m2m()
            return HttpResponseRedirect(reverse("project",args=(project_id,)))
    else:
        initial_values = {}
        if assembly_id:
            current_assembly = get_object_or_404(Assembly, pk=assembly_id)
            initial_values['assembly'] = current_assembly
        form = PartForm(initial=initial_values)
        
    context['form']= form
    return render(request, "newobject.html", context)

@login_required
def project(request, project_id):
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
            parts_list.append(part)

    context = {"project": current_project,
               "assembly_list": assembly_list,
               "parts_list": parts_list,
               }

    return render(request, "project.html", context)

@login_required
def assembly_view(request, project_id, assembly_id):
    current_project = get_object_or_404(Project, pk=project_id)
    current_assembly = get_object_or_404(Assembly, pk=assembly_id)
    assembly_list = current_assembly.sub.all()
    parts_list = []
    for part in current_assembly.part_set.all():
        parts_list.append(part)

    context = {"project": current_project,
               "c_assembly": current_assembly,
               "assembly_list": assembly_list,
               "parts_list": parts_list,
               }

    return render(request, "assembly.html", context)

@login_required
def part(request, project_id, assembly_id, part_id):
    current_project = get_object_or_404(Project, pk=project_id)
    current_assembly = get_object_or_404(Assembly, pk=assembly_id)
    current_part = get_object_or_404(Part, pk=part_id)
    context = {"project": current_project,
               "assembly": current_assembly,
               "part": current_part,
               }

    return render(request, "part.html", context)
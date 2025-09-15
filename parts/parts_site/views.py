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
            form = PartFormEdit(request.POST, request.FILES, instance=get_object_or_404(Part, pk=part_id,))
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
            form = PartFormEdit(instance=get_object_or_404(Part, pk=part_id))
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
            part.save()
            form.save_m2m()
            
            # Create initial revision
            initial_revision = PartRevision.objects.create(
                part=part,
                revision_number='A',
                status=PartStatus.NEW
            )
            
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
            # Add revision info to each part
            if part.latest_revision:
                part.current_status = part.latest_revision.status
                part.current_status_display = part.latest_revision.get_status_display()
                part.current_mfg_type = part.latest_revision.mfg_type
                part.current_mfg_type_display = part.latest_revision.get_mfg_type_display()
                part.current_material = part.latest_revision.material
                part.current_quantity = part.latest_revision.quantity
                part.current_drawing = part.latest_revision.drawing
            else:
                part.current_status = None
                part.current_status_display = "No revisions"
                part.current_mfg_type = None
                part.current_mfg_type_display = "Not specified"
                part.current_material = None
                part.current_quantity = None
                part.current_drawing = None
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
        # Add revision info to each part
        if part.latest_revision:
            part.current_status = part.latest_revision.status
            part.current_status_display = part.latest_revision.get_status_display()
            part.current_mfg_type = part.latest_revision.mfg_type
            part.current_mfg_type_display = part.latest_revision.get_mfg_type_display()
            part.current_material = part.latest_revision.material
            part.current_quantity = part.latest_revision.quantity
            part.current_drawing = part.latest_revision.drawing
        else:
            part.current_status = None
            part.current_status_display = "No revisions"
            part.current_mfg_type = None
            part.current_mfg_type_display = "Not specified"
            part.current_material = None
            part.current_quantity = None
            part.current_drawing = None
        parts_list.append(part)

    context = {"project": current_project,
               "c_assembly": current_assembly,
               "assembly_list": assembly_list,
               "parts_list": parts_list,
               }

    return render(request, "assembly.html", context)

@login_required
def part(request, project_id, assembly_id, part_id, revision_id=None):
    current_project = get_object_or_404(Project, pk=project_id)
    current_assembly = get_object_or_404(Assembly, pk=assembly_id)
    current_part = get_object_or_404(Part, pk=part_id)
    
    # Get the revision - either the specified one or the latest
    if revision_id:
        current_revision = get_object_or_404(PartRevision, pk=revision_id, part=current_part)
    else:
        current_revision = current_part.latest_revision
    
    # Get all revisions for the dropdown, ordered by revision letter
    revisions = current_part.revisions.order_by('-revision_number')
    
    # Check if user can delete revisions
    can_delete_revisions = (request.user.groups.filter(name='leads').exists() or 
                           request.user.groups.filter(name='mentors').exists())
    
    context = {"project": current_project,
               "assembly": current_assembly,
               "part": current_part,
               "revision": current_revision,
               "revisions": revisions,
               "can_delete_revisions": can_delete_revisions,
               }

    return render(request, "part.html", context)

@login_required
def newrevision(request, project_id, assembly_id, part_id):
    context = {}
    current_part = get_object_or_404(Part, pk=part_id)
    
    if request.method == "POST":
        form = PartRevisionCreateForm(request.POST, request.FILES, user=request.user)
        
        if form.is_valid():
            revision = form.save(commit=False)
            revision.part = current_part
            revision.save()
            return HttpResponseRedirect(reverse("part", args=(project_id, assembly_id, part_id)))
    else:
        # Set default revision number
        latest_revision = current_part.revisions.order_by('-revision_number').first()
        if latest_revision:
            # Increment revision letter
            next_revision = chr(ord(latest_revision.revision_number) + 1)
        else:
            next_revision = 'A'
        
        form = PartRevisionCreateForm(user=request.user, initial={'revision_number': next_revision})
    
    context['form'] = form
    context['part'] = current_part
    return render(request, "newobject.html", context)

@login_required
def editrevision(request, project_id, assembly_id, part_id, revision_id):
    context = {}
    current_revision = get_object_or_404(PartRevision, pk=revision_id, part_id=part_id)
    
    if request.method == "POST":
        form = PartRevisionForm(request.POST, request.FILES, user=request.user, instance=current_revision)
        
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse("part_revision", args=(project_id, assembly_id, part_id, revision_id)))
    else:
        form = PartRevisionForm(user=request.user, instance=current_revision)
    
    context['form'] = form
    context['part'] = current_revision.part
    context['revision'] = current_revision
    return render(request, "editobject.html", context)

@login_required
def deleterevision(request, project_id, assembly_id, part_id, revision_id):
    current_revision = get_object_or_404(PartRevision, pk=revision_id, part_id=part_id)
    current_part = current_revision.part
    
    # Check if user has permission to delete revisions
    if not (request.user.groups.filter(name='leads').exists() or 
            request.user.groups.filter(name='mentors').exists()):
        from django.contrib import messages
        messages.error(request, "Only leads and mentors can delete revisions.")
        return HttpResponseRedirect(reverse("part", args=(project_id, assembly_id, part_id)))
    
    # Check if this is the only revision
    if current_part.revisions.count() <= 1:
        from django.contrib import messages
        messages.error(request, "Cannot delete the last revision of a part.")
        return HttpResponseRedirect(reverse("part", args=(project_id, assembly_id, part_id)))
    
    # Check if this is the latest revision
    if current_part.latest_revision == current_revision:
        # Find the next latest revision
        next_latest = current_part.revisions.exclude(id=revision_id).first()
        if next_latest:
            current_part.latest_revision = next_latest
            current_part.save()
    
    # Delete the revision
    current_revision.delete()
    
    from django.contrib import messages
    messages.success(request, f"Revision {current_revision.revision_number} has been deleted.")
    
    return HttpResponseRedirect(reverse("part", args=(project_id, assembly_id, part_id)))
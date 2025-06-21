from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.conf import settings
from datetime import datetime
from collections import defaultdict
from django.contrib.admin.views.decorators import staff_member_required
from django.http import Http404
from django.views.decorators.http import require_POST

# --- CORRECT IMPORTS ---
from resources.models import Resource, Semester, Year
from .forms import ResourceUploadForm


def Sem1(request, semester_id):
    res = Resource.objects.filter(semester_id=semester_id).exclude(resource_type='Syllabus')
    sub = res.values('subject').distinct()
    return render(request, 'resources/sem.html', {'sub': sub, 'res': res})


def Y1(request):
    year_obj = get_object_or_404(Year, year='Year 1')
    sem = Semester.objects.filter(year=year_obj).order_by('semester')
    return render(request,'resources/Y1.html',{'sem':sem})

def Y2(request):
    year_obj = get_object_or_404(Year, year='Year 2')
    sem = Semester.objects.filter(year=year_obj).order_by('semester')
    return render(request,'resources/Y2.html',{'sem':sem})

def Y3(request):
    year_obj = get_object_or_404(Year, year='Year 3')
    sem = Semester.objects.filter(year=year_obj).order_by('semester')
    return render(request,'resources/Y3.html',{'sem':sem})


# Lowercased lookup dict once for performance
YEAR_LABEL_MAP = {
    'BHCS-Y-1': 'Year 1',
    'BHCS-Y-2': 'Year 2',
    'BHCS-Y-3': 'Year 3',
}

SUBJECT_LOOKUP = {k.lower(): v for k, v in Resource.SEMESTER_SUBJECTS.items()}


def format_semester_key(sem_obj):
    sem_label = sem_obj.semester.split(' | ')[0]
    year_label = sem_obj.year.year
    return f"{sem_label} | {year_label}"


@staff_member_required
def upload_resource_view(request, semester_id):

    subject = request.GET.get('subject')
    year = request.GET.get('year') # This is the resource_file_year, for PYQs
    rtype = request.GET.get('type')

    # Get the Semester object
    semester_obj = get_object_or_404(Semester, id=semester_id)

    if request.method == "POST":
        form = ResourceUploadForm(request.POST, request.FILES)
        if form.is_valid():
            resource_instance = form.save(commit=False)
            resource_instance.semester = semester_obj
            resource_instance.save()
            return redirect('resources:add')
    else:
        # Pre-fill the form with initial data based on URL parameters
        initial_data = {
            'semester': semester_obj,
            'subject': subject,
            'resource_type': rtype
        }

        if rtype == "PYQs" and year and year != "N/A":
            try:
                initial_data['resource_file_year'] = int(year)
            except (ValueError, TypeError):
                initial_data['resource_file_year'] = None
        else:
            initial_data['resource_file_year'] = None

        form = ResourceUploadForm(initial=initial_data)

    return render(request, "resources/upload_form.html", {"form": form})

@staff_member_required
def ignore_resource(request, resource_id):
    resource = get_object_or_404(Resource, id=resource_id)
    if request.method == "POST":
        resource.is_ignored = not resource.is_ignored
        resource.save()
        return redirect('resources:add')
    else:
        return redirect('resources:add')

@staff_member_required
@require_POST
def ignore_non_existent_resource(request):
    semester_id = request.POST.get('semester_id')
    subject = request.POST.get('subject')
    resource_type = request.POST.get('resource_type')
    year_str = request.POST.get('year')


    # Ensure semester_id is convertible to int before get_object_or_404
    if semester_id: # Check if it's not None or empty string
        try:
            semester_id = int(semester_id) # Explicitly convert to int
        except (ValueError, TypeError):

            return redirect('resources:add') # Redirect if ID is invalid. Don't raise 404.

    try:
        semester = get_object_or_404(Semester, id=semester_id)
    except Http404:

        return redirect('resources:add') # Redirect if semester not found

    try:
        Resource.objects.create(
            semester=semester,
            subject=subject,
            resource_type=resource_type,
            resource_file_year=int(year_str) if year_str and year_str.isdigit() else None, # Convert year
            is_ignored=True
        )

    except Exception as e:
        print(f"DEBUG_IGNORE_VIEW: Error creating ignored resource: {e}")
        # Optionally, add Django messages here for user feedback
        # messages.error(request, f"Failed to ignore resource: {e}")

    return redirect('resources:add') # <--- This redirect is the target


@staff_member_required
def edit_resource(request, resource_id):
    resource = get_object_or_404(Resource, id=resource_id)
    if request.method == "POST":
        form = ResourceUploadForm(request.POST, request.FILES, instance=resource)
        if form.is_valid():
            form.save()
            return redirect('resources:add')
    else:
        form = ResourceUploadForm(instance=resource)

    return render(request, 'resources/edit_resource.html', {'form': form, 'resource': resource})

@staff_member_required
def delete_resource(request, resource_id):
    resource = get_object_or_404(Resource, id=resource_id)
    resource.delete()
    return redirect('resources:add')

@staff_member_required
def add(request):


    if not request.user.is_staff:
        raise Http404("This page doesn't exist")
    current_year = datetime.now().year
    years = list(range(2020, current_year + 1))

    # Initialize data structures
    truly_missing_resources = defaultdict(lambda: defaultdict(list))
    ignored_resources = defaultdict(lambda: defaultdict(list))

    total_truly_missing_items = 0
    total_ignored_items = 0
    total_expected_items = 0

    truly_missing_resource_type_totals = defaultdict(int)
    ignored_resource_type_totals = defaultdict(int)
    truly_missing_semester_totals = defaultdict(int)
    ignored_semester_totals = defaultdict(int)

    unique_resource_types_truly_missing = set()
    unique_semesters_with_truly_missing = set()
    unique_resource_types_ignored = set()
    unique_semesters_with_ignored = set()

    available_resources = defaultdict(list) # This will now store truly 'available' items

    debug_info = {
        'total_subjects_checked': 0,
        'total_resources_checked': 0,
        'missing_by_type': defaultdict(int),
        'missing_by_semester': defaultdict(int),
        'missing_by_year': defaultdict(int),
        'expected_by_type': defaultdict(int),
        'expected_by_semester': defaultdict(int),
        'ignored_by_type': defaultdict(int),
        'ignored_by_semester': defaultdict(int),
    }

    all_semesters = Semester.objects.all().order_by('id')

    for sem in all_semesters:
        sem_key = format_semester_key(sem).lower()
        subject_choices = SUBJECT_LOOKUP.get(sem_key, [])
        debug_info['total_subjects_checked'] += len(subject_choices)

        for _, subject_name in subject_choices:
            expected_pyqs_count = len(years)
            expected_book_count = 1
            expected_video_count = 1

            total_expected_items += (expected_pyqs_count + expected_book_count + expected_video_count)
            debug_info['expected_by_type']['PYQs'] += expected_pyqs_count
            debug_info['expected_by_type']['BOOK'] += expected_book_count
            debug_info['expected_by_type']['Youtube Video URL'] += expected_video_count
            debug_info['expected_by_semester'][sem.semester] += (expected_pyqs_count + expected_book_count + expected_video_count)

            # --- Process PYQs ---
            for year_val in years:
                existing_pyq = Resource.objects.filter(
                    semester=sem, subject=subject_name,
                    resource_type='PYQs', resource_file_year=year_val
                ).first()

                debug_info['total_resources_checked'] += 1



                # Determine if the resource has actual content (file/URL)
                has_content_pyq = existing_pyq and (existing_pyq.resource_file or existing_pyq.resource_url)

                if not existing_pyq: # Truly missing (not in DB)
                    item_data = {
                        "subject": subject_name,
                        "year": year_val,
                        "semester_id": sem.id,
                        "semester_name": sem.semester,
                        "resource_type": "PYQs",
                        "resource_id": None,
                        "is_ignored": False,
                    }
                    truly_missing_resources['PYQs'][sem.semester].append(item_data)
                    truly_missing_resource_type_totals['PYQs'] += 1
                    truly_missing_semester_totals[sem.id] += 1
                    total_truly_missing_items += 1
                    unique_resource_types_truly_missing.add('PYQs')
                    unique_semesters_with_truly_missing.add(sem.id)
                    debug_info['missing_by_type']['PYQs'] += 1
                    debug_info['missing_by_semester'][sem.semester] += 1
                    debug_info['missing_by_year'][year_val] += 1

                elif existing_pyq.is_ignored: # Exists but is ignored (goes to Ignored section)
                    item_data = {
                        "subject": subject_name,
                        "year": year_val,
                        "semester_id": sem.id,
                        "semester_name": sem.semester,
                        "resource_type": "PYQs",
                        "resource_id": existing_pyq.id,
                        "is_ignored": True,
                    }
                    ignored_resources['PYQs'][sem.semester].append(item_data)
                    ignored_resource_type_totals['PYQs'] += 1
                    ignored_semester_totals[sem.id] += 1
                    total_ignored_items += 1
                    unique_resource_types_ignored.add('PYQs')
                    unique_semesters_with_ignored.add(sem.id)
                    debug_info['ignored_by_type']['PYQs'] += 1
                    debug_info['ignored_by_semester'][sem.semester] += 1

                elif has_content_pyq: # Exists, NOT ignored, AND has content (goes to Available section)
                    available_resources[sem.semester].append({
                        "id": existing_pyq.id,
                        "subject": subject_name,
                        "resource_type": "PYQs",
                        "year": year_val,
                        "created_at": existing_pyq.created_at,
                        "semester_id": sem.id,
                        "is_ignored": False
                    })

                else: # Exists, NOT ignored, AND has NO content (goes to Missing section, needs upload)
                    item_data = {
                        "subject": subject_name,
                        "year": year_val,
                        "semester_id": sem.id,
                        "semester_name": sem.semester,
                        "resource_type": "PYQs",
                        "resource_id": existing_pyq.id, # Pass existing ID
                        "is_ignored": False, # Explicitly false
                    }
                    truly_missing_resources['PYQs'][sem.semester].append(item_data)
                    truly_missing_resource_type_totals['PYQs'] += 1
                    truly_missing_semester_totals[sem.id] += 1
                    total_truly_missing_items += 1 # Increment missing count
                    unique_resource_types_truly_missing.add('PYQs')
                    unique_semesters_with_truly_missing.add(sem.id)
                    debug_info['missing_by_type']['PYQs'] += 1
                    debug_info['missing_by_semester'][sem.semester] += 1
                    debug_info['missing_by_year'][year_val] += 1



            # --- Process BOOK ---
            existing_book = Resource.objects.filter(
                semester=sem, subject=subject_name, resource_type='BOOK'
            ).first()

            debug_info['total_resources_checked'] += 1
            has_content_book = existing_book and (existing_book.resource_file or existing_book.resource_url)



            if not existing_book: # Truly missing (not in DB)
                item_data = {
                    "subject": subject_name,
                    "year": "N/A",
                    "semester_id": sem.id,
                    "semester_name": sem.semester,
                    "resource_type": "BOOK",
                    "resource_id": None,
                    "is_ignored": False,
                }
                truly_missing_resources['BOOK'][sem.semester].append(item_data)
                truly_missing_resource_type_totals['BOOK'] += 1
                truly_missing_semester_totals[sem.id] += 1
                total_truly_missing_items += 1
                unique_resource_types_truly_missing.add('BOOK')
                unique_semesters_with_truly_missing.add(sem.id)
                debug_info['missing_by_type']['BOOK'] += 1
                debug_info['missing_by_semester'][sem.semester] += 1

            elif existing_book.is_ignored: # Exists but is ignored (goes to Ignored section)
                item_data = {
                    "subject": subject_name,
                    "year": "N/A",
                    "semester_id": sem.id,
                    "semester_name": sem.semester,
                    "resource_type": "BOOK",
                    "resource_id": existing_book.id,
                    "is_ignored": True,
                }
                ignored_resources['BOOK'][sem.semester].append(item_data)
                ignored_resource_type_totals['BOOK'] += 1
                ignored_semester_totals[sem.id] += 1
                total_ignored_items += 1
                unique_resource_types_ignored.add('BOOK')
                unique_semesters_with_ignored.add(sem.id)
                debug_info['ignored_by_type']['BOOK'] += 1
                debug_info['ignored_by_semester'][sem.semester] += 1

            elif has_content_book: # Exists, NOT ignored, AND has content (goes to Available section)
                available_resources[sem.semester].append({
                    "id": existing_book.id,
                    "subject": subject_name,
                    "resource_type": "BOOK",
                    "year": "N/A",
                    "created_at": existing_book.created_at,
                    "semester_id": sem.id,
                    "is_ignored": False
                })
                print(f"  -> Categorized as AVAILABLE (exists, not ignored, has content).")
            else: # Exists, NOT ignored, AND has NO content (goes to Missing section, needs upload)
                item_data = {
                    "subject": subject_name,
                    "year": "N/A",
                    "semester_id": sem.id,
                    "semester_name": sem.semester,
                    "resource_type": "BOOK",
                    "resource_id": existing_book.id,
                    "is_ignored": False,
                }
                truly_missing_resources['BOOK'][sem.semester].append(item_data)
                truly_missing_resource_type_totals['BOOK'] += 1
                truly_missing_semester_totals[sem.id] += 1
                total_truly_missing_items += 1
                unique_resource_types_truly_missing.add('BOOK')
                unique_semesters_with_truly_missing.add(sem.id)
                debug_info['missing_by_type']['BOOK'] += 1
                debug_info['missing_by_semester'][sem.semester] += 1
                print(f"  -> Categorized as MISSING (exists, not ignored, NO content). total_truly_missing_items: {total_truly_missing_items}")

            # --- Process Youtube Video URL ---
            existing_video = Resource.objects.filter(
                semester=sem, subject=subject_name, resource_type='Youtube Video URL'
            ).first()

            debug_info['total_resources_checked'] += 1
            # Note: For Youtube Video URL, 'has_content' means resource_url is not empty
            has_content_video = existing_video and existing_video.resource_url

            print(f"\nProcessing Video: {subject_name} (Sem {sem.semester})")
            print(f"  - existing_video: {existing_video}")
            print(f"  - existing_video.is_ignored (if exists): {existing_video.is_ignored if existing_video else 'N/A'}")

            if not existing_video: # Truly missing (not in DB)
                item_data = {
                    "subject": subject_name,
                    "year": "N/A",
                    "semester_id": sem.id,
                    "semester_name": sem.semester,
                    "resource_type": "Youtube Video URL",
                    "resource_id": None,
                    "is_ignored": False,
                }
                truly_missing_resources['Youtube Video URL'][sem.semester].append(item_data)
                truly_missing_resource_type_totals['Youtube Video URL'] += 1
                truly_missing_semester_totals[sem.id] += 1
                total_truly_missing_items += 1
                unique_resource_types_truly_missing.add('Youtube Video URL')
                unique_semesters_with_truly_missing.add(sem.id)
                debug_info['missing_by_type']['Youtube Video URL'] += 1
                debug_info['missing_by_semester'][sem.semester] += 1
                print(f"  -> Categorized as TRULY MISSING (no DB entry). total_truly_missing_items: {total_truly_missing_items}")
            elif existing_video.is_ignored: # Exists but is ignored (goes to Ignored section)
                item_data = {
                    "subject": subject_name,
                    "year": "N/A",
                    "semester_id": sem.id,
                    "semester_name": sem.semester,
                    "resource_type": "Youtube Video URL",
                    "resource_id": existing_video.id,
                    "is_ignored": True,
                }
                ignored_resources['Youtube Video URL'][sem.semester].append(item_data)
                ignored_resource_type_totals['Youtube Video URL'] += 1
                ignored_semester_totals[sem.id] += 1
                total_ignored_items += 1
                unique_resource_types_ignored.add('Youtube Video URL')
                unique_semesters_with_ignored.add(sem.id)
                debug_info['ignored_by_type']['Youtube Video URL'] += 1
                debug_info['ignored_by_semester'][sem.semester] += 1
                print(f"  -> Categorized as IGNORED. total_ignored_items: {total_ignored_items}")
            elif has_content_video: # Exists, NOT ignored, AND has content (goes to Available section)
                available_resources[sem.semester].append({
                    "id": existing_video.id,
                    "subject": subject_name,
                    "resource_type": "Youtube Video URL",
                    "year": "N/A",
                    "created_at": existing_video.created_at,
                    "semester_id": sem.id,
                    "is_ignored": False
                })
                print(f"  -> Categorized as AVAILABLE (exists, not ignored, has content).")
            else: # Exists, NOT ignored, AND has NO content (goes to Missing section, needs upload)
                item_data = {
                    "subject": subject_name,
                    "year": "N/A",
                    "semester_id": sem.id,
                    "semester_name": sem.semester,
                    "resource_type": "Youtube Video URL",
                    "resource_id": existing_video.id,
                    "is_ignored": False,
                }
                truly_missing_resources['Youtube Video URL'][sem.semester].append(item_data)
                truly_missing_resource_type_totals['Youtube Video URL'] += 1
                truly_missing_semester_totals[sem.id] += 1
                total_truly_missing_items += 1
                unique_resource_types_truly_missing.add('Youtube Video URL')
                unique_semesters_with_truly_missing.add(sem.id)
                debug_info['missing_by_type']['Youtube Video URL'] += 1
                debug_info['missing_by_semester'][sem.semester] += 1
                print(f"  -> Categorized as MISSING (exists, not ignored, NO content). total_truly_missing_items: {total_truly_missing_items}")


    # Sort available resources
    final_available_resources = {}
    if available_resources:
        for semester_name, resources_list in available_resources.items():
            final_available_resources[semester_name] = sorted(resources_list, key=lambda x: (x['subject'], x['resource_type'], x['year']))
    print(f"\n--- Final Counts before Context ---")
    print(f"Total Expected Items: {total_expected_items}")
    print(f"Total Truly Missing Items: {total_truly_missing_items}")
    print(f"Total Ignored Items: {total_ignored_items}")
    print(f"Total Available Items (final list): {sum(len(l) for l in final_available_resources.values())}")


    # Calculate completion percentage
    completion_percentage = 0
    # Expected - (Truly Missing that needs upload + Ignored)
    fulfilled_items = total_expected_items - total_truly_missing_items - total_ignored_items
    if total_expected_items > 0:
        completion_percentage = round((fulfilled_items / total_expected_items) * 100, 1)

    # Organize and sort the data for TRULY MISSING resources (for "Missing Resources" section)
    final_grouped_cards_truly_missing = {}
    for rtype, sem_dict in truly_missing_resources.items():
        sorted_semesters_by_number = sorted(
            sem_dict.items(),
            key=lambda x: Semester.objects.get(semester=x[0]).id
        )
        final_grouped_cards_truly_missing[rtype] = {
            'semesters': dict(sorted_semesters_by_number),
            'total_items': truly_missing_resource_type_totals[rtype],
            'expected_items': debug_info['expected_by_type'][rtype],
            'completion_percentage': round(((debug_info['expected_by_type'][rtype] - truly_missing_resource_type_totals[rtype]) / debug_info['expected_by_type'][rtype]) * 100, 1) if debug_info['expected_by_type'][rtype] > 0 else 0
        }
    final_grouped_cards_truly_missing = dict(sorted(
        final_grouped_cards_truly_missing.items(),
        key=lambda x: x[1]['total_items'],
        reverse=True
    ))

    # Organize and sort the data for IGNORED resources (for "Ignored Resources" section)
    final_grouped_cards_ignored = {}
    for rtype, sem_dict in ignored_resources.items():
        sorted_semesters_by_number = sorted(
            sem_dict.items(),
            key=lambda x: Semester.objects.get(semester=x[0]).id
        )
        final_grouped_cards_ignored[rtype] = {
            'semesters': dict(sorted_semesters_by_number),
            'total_items': ignored_resource_type_totals[rtype],
            'expected_items': debug_info['expected_by_type'][rtype],
            'completion_percentage': round(((debug_info['expected_by_type'][rtype] - ignored_resource_type_totals[rtype]) / debug_info['expected_by_type'][rtype]) * 100, 1) if debug_info['expected_by_type'][rtype] > 0 else 0
        }
    final_grouped_cards_ignored = dict(sorted(
        final_grouped_cards_ignored.items(),
        key=lambda x: x[1]['total_items'],
        reverse=True
    ))

    # Prepare semester dropdown data for missing resources (truly missing)
    semesters_for_missing_dropdown = [
        {
            'number': sem.id,
            'name': sem.semester,
            'total_missing': truly_missing_semester_totals[sem.id],
            'expected_items': debug_info['expected_by_semester'][sem.semester],
            'completion_percentage': round(((debug_info['expected_by_semester'][sem.semester] - truly_missing_semester_totals[sem.id]) / debug_info['expected_by_semester'][sem.semester]) * 100, 1) if debug_info['expected_by_semester'][sem.semester] > 0 else 0
        }
        for sem in all_semesters if sem.id in unique_semesters_with_truly_missing
    ]
    semesters_for_missing_dropdown.sort(key=lambda x: x['number'])

    # Prepare semester dropdown data for ignored resources
    semesters_for_ignored_dropdown = [
        {
            'number': sem.id,
            'name': sem.semester,
            'total_ignored': ignored_semester_totals[sem.id],
            'expected_items': debug_info['expected_by_semester'][sem.semester],
            'completion_percentage': round(((debug_info['expected_by_semester'][sem.semester] - ignored_semester_totals[sem.id]) / debug_info['expected_by_semester'][sem.semester]) * 100, 1) if debug_info['expected_by_semester'][sem.semester] > 0 else 0
        }
        for sem in all_semesters if sem.id in unique_semesters_with_ignored
    ]
    semesters_for_ignored_dropdown.sort(key=lambda x: x['number'])
    
    total_available_items = sum(len(l) for l in final_available_resources.values()) # Correctly sum items in final_available_resources

    context = {
        "missing_resources_grouped_cards": final_grouped_cards_truly_missing,
        "ignored_resources_grouped_cards": final_grouped_cards_ignored,
        "available_resources": final_available_resources,
        "total_missing_items": total_truly_missing_items,
        "total_ignored_items": total_ignored_items,
        "total_available_items": total_available_items,
        "total_expected_items": total_expected_items,
        "overall_completion_percentage": completion_percentage,
        "total_resource_types": len(Resource.RESOURCE_TYPE),
        "affected_semesters_count": len(unique_semesters_with_truly_missing.union(unique_semesters_with_ignored)),
        "semesters_for_dropdown": semesters_for_missing_dropdown,
        "semesters_for_ignored_dropdown": semesters_for_ignored_dropdown,
        "Resource": Resource,
        "all_semesters": all_semesters,
        "debug_info": {
            'total_subjects_checked': debug_info['total_subjects_checked'],
            'total_resources_checked': debug_info['total_resources_checked'],
            'missing_by_type': dict(debug_info['missing_by_type']),
            'missing_by_semester': dict(debug_info['missing_by_semester']),
            'missing_by_year': dict(debug_info['missing_by_year']),
            'expected_by_type': dict(debug_info['expected_by_type']),
            'expected_by_semester': dict(debug_info['expected_by_semester']),
            'ignored_by_type': dict(debug_info['ignored_by_type']),
            'ignored_by_semester': dict(debug_info['ignored_by_semester']),
        }
    }
    print("--- add view: End ---")
    return render(request, "resources/add.html", context)
from random import randint

from . import util

from django import forms
from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.urls import reverse


class NewEditForm(forms.Form):
    contents = forms.CharField(label="Contents", widget=forms.Textarea)

class NewCreateForm(forms.Form):
    title = forms.CharField(label="Title", max_length=100)
    contents = forms.CharField(label="Contents", widget=forms.Textarea)

class NewSearchForm(forms.Form):
    query = forms.CharField(label="Search", max_length=100, widget=forms.TextInput(
        attrs={'placeholder': 'Search Encyclopedia'}))

def index(request):
    """ Homepage """
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

def view_entry(request, entry):
    """ Display an entry's page, or an error if not found """
    if util.get_entry(entry):
        return render(request, "encyclopedia/entry.html", {
            "entry": entry,
            "contents": util.convert_md(entry),
            "title": util.get_title(entry)
        })
    else:
        return render(request, "encyclopedia/error.html", {
            "error": "404 Error, this page does not exist"
        })

def edit_entry(request, entry):
    """ Allow a user to edit an entry """
    if request.method == "POST":
        # Create a form instance and populate it with data from the request
        form = NewEditForm(request.POST)
       
        # Check whether form is valid
        if form.is_valid():
            # Update contents/create new file and redirect
            contents = form.cleaned_data['contents'].replace("\n", "")
            util.edit_entry(entry, contents)
            return redirect(reverse('viewEntry', kwargs={'entry': entry}))
        else:
            title = util.get_title(entry)
            contents = util.read_contents(entry)
            form = NewEditForm({"title": title, "contents": contents})
            return render(request, "encyclopedia/edit.html", {
                "form": form,
                "entry": entry,
                "title": title
            })
    else:
        if util.get_entry(entry):
            title = util.get_title(entry)
            contents = util.read_contents(entry)
            form = NewEditForm({"title": title, "contents": contents})
            return render(request, "encyclopedia/edit.html", {
                "form": form,
                "entry": entry,
                "title": title
            })
        else:
            return render(request, "encyclopedia/error.html", {
                "error": "404 Error, this page does not exist"
            })

def create_entry(request):
    """ Allow a user to create an entry """
    if request.method == "POST":
        # Create a form instance and populate it with data from the request
        form = NewCreateForm(request.POST)

        # Check whether form is valid
        if form.is_valid():
            title = form.cleaned_data['title']
            contents = form.cleaned_data['contents'].replace("\n", "")

            # Display error that name already exists
            if util.create_entry(title, contents):
                return redirect(index)
            else:
                return render(request, "encyclopedia/error.html", {
                    "error": "Error, this page already exists"
                })
    else:
        form = NewCreateForm()
        
    return render(request, "encyclopedia/create.html", {
        "form": form
    })

def random_entry(request):
    """ Generate a page for a random entry """
    entries = util.list_entries()
    randEntry = randint(0, len(entries) - 1)
    return redirect(reverse('viewEntry', kwargs={'entry': entries[randEntry]}))

def search_entry(request):
    query = request.GET.get('q')
    check = util.get_entry(query)

    # Check if entry exists
    if check:
        return redirect(reverse('viewEntry', kwargs={"entry": query}))
    else:
        # Check for substring matches, and return if found
        # Otherwise, return an error page
        entries = util.list_entries()
        matches = []
        for entry in entries:
            if query.lower() in entry.lower():
                matches.append(entry)
        if matches:
            return render(request, "encyclopedia/results.html", {
                "matches": matches
            })
        else:
            return render(request, "encyclopedia/error.html", {
                "error": f"Error, no matching entries found for '{query}'"
            })  

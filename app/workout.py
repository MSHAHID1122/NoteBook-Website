from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from .models import WorkoutNote, Folder
from . import db

workout = Blueprint('workout', __name__)
@workout.route('/notes', methods=['GET', 'POST'])
@login_required
def notes():
    if request.method == 'POST':
        content = request.form.get('content')
        folder_id = request.form.get('folder_id')
        if not content:
            flash('Content cannot be empty!')
        else:
            new_note = WorkoutNote(content=content, user_id=current_user.id, folder_id=folder_id)
            db.session.add(new_note)
            db.session.commit()
            flash('Note added successfully!')
        return redirect(url_for('workout.notes'))
    
    folders = Folder.query.filter_by(user_id=current_user.id).all()
    notes = WorkoutNote.query.filter_by(user_id=current_user.id, folder_id=None).all()
    return render_template('notes.html', folders=folders, notes=notes)

@workout.route('/create_folder', methods=['POST'])
@login_required
def create_folder():
    folder_name = request.form.get('folder_name')
    if folder_name:
        new_folder = Folder(name=folder_name, user_id=current_user.id)
        db.session.add(new_folder)
        db.session.commit()
        flash('Folder created successfully!')
    return redirect(url_for('workout.notes'))

@workout.route('/folder/<int:folder_id>', methods=['GET', 'POST'])
@login_required
def view_folder(folder_id):
    folder = Folder.query.get_or_404(folder_id)
    if folder.user_id != current_user.id:
        flash('You do not have permission to view this folder.')
        return redirect(url_for('workout.notes'))
    
    if request.method == 'POST':
        content = request.form.get('content')
        if not content:
            flash('Content cannot be empty!')
        else:
            new_note = WorkoutNote(content=content, user_id=current_user.id, folder_id=folder_id)
            db.session.add(new_note)
            db.session.commit()
            flash('Note added successfully!')
        return redirect(url_for('workout.view_folder', folder_id=folder_id))
    
    notes = WorkoutNote.query.filter_by(user_id=current_user.id, folder_id=folder_id).all()
    return render_template('folder.html', folder=folder, notes=notes)
@workout.route('/view_note/<int:id>', methods=['GET'])
@login_required
def view_note(id):
    note = WorkoutNote.query.get_or_404(id)
    if note.user_id != current_user.id:
        flash('You do not have permission to view this note.')
        return redirect(url_for('workout.notes'))
    return render_template('view_note.html', note=note)
@workout.route('/edit_note/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_note(id):
    note = WorkoutNote.query.get_or_404(id)
    if note.user_id != current_user.id:
        flash('You do not have permission to edit this note.')
        return redirect(url_for('workout.notes'))

    if request.method == 'POST':
        content = request.form.get('content')
        if not content:
            flash('Content cannot be empty!')
        else:
            note.content = content
            db.session.commit()
            flash('Note updated successfully!')
        return redirect(url_for('workout.view_note', id=note.id))

    return render_template('edit_note.html', note=note) 
@workout.route('/delete_note/<int:id>', methods=['POST'])
@login_required
def delete_note(id):
    note = WorkoutNote.query.get_or_404(id)
    if note.user_id != current_user.id:
        flash('You do not have permission to delete this note.')
        return redirect(url_for('workout.notes'))

    db.session.delete(note)
    db.session.commit()
    flash('Note deleted successfully!')
    return redirect(url_for('workout.notes'))
@workout.route('/delete_folder/<int:id>', methods=['POST'])
@login_required
def delete_folder(id):
    folder = Folder.query.get_or_404(id)
    if folder.user_id != current_user.id:
        flash('You do not have permission to delete this folder.')
        return redirect(url_for('workout.notes'))

    # Delete all notes in the folder first
    notes = WorkoutNote.query.filter_by(folder_id=id).all()
    for note in notes:
        db.session.delete(note)

    db.session.delete(folder)
    db.session.commit()
    flash('Folder and its notes deleted successfully!')
    return redirect(url_for('workout.notes'))


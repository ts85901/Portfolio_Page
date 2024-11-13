from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from flask_login import login_required, current_user
from app import app, db
from models import Project, ProjectFile
import os
from werkzeug.utils import secure_filename
from utils import allowed_file

UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/project/<int:id>')
def view_project(id):
    project = Project.query.get_or_404(id)
    return render_template('project_detail.html', project=project)

@app.route('/admin/project/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_project(id):
    if not current_user.is_admin:
        return redirect(url_for('index'))

    project = Project.query.get_or_404(id)

    if request.method == 'POST':
        project.title = request.form.get('title')
        project.description = request.form.get('description')
        project.short_description = request.form.get('short_description')
        project.tech_stack = request.form.get('tech_stack')
        project.project_url = request.form.get('project_url')

        # Handle file uploads
        if 'files[]' in request.files:
            files = request.files.getlist('files[]')
            for file in files:
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(file_path)

                    project_file = ProjectFile(
                        filename=filename,
                        file_type=filename.rsplit('.', 1)[1].lower(),
                        file_path=file_path,
                        project=project
                    )
                    db.session.add(project_file)

        db.session.commit()
        return redirect(url_for('view_project', id=project.id))

    return render_template('edit_project.html', project=project)

@app.route('/admin/project/delete/<int:id>')
@login_required
def delete_project(id):
    if not current_user.is_admin:
        return redirect(url_for('index'))

    project = Project.query.get_or_404(id)

    # Delete associated files
    for file in project.files:
        try:
            os.remove(file.file_path)
        except:
            pass
        db.session.delete(file)

    db.session.delete(project)
    db.session.commit()

    return redirect(url_for('admin'))

@app.route('/file/download/<int:file_id>')
def download_file(file_id):
    file = ProjectFile.query.get_or_404(file_id)
    return send_file(file.file_path, as_attachment=True)
"""
Routes for the Mwananchi System.

Organised into two blueprints:
  - main_bp  : public-facing pages (home, submit/track complaints, budget)
  - admin_bp : authenticated admin dashboard (prefixed with /admin)
"""
import csv
import io
from datetime import datetime

from flask import (
    Blueprint, render_template, redirect, url_for, flash, request,
    Response, abort,
)
from flask_login import login_user, logout_user, login_required, current_user
from sqlalchemy import or_

from app import db
from app.models import Complaint, Budget, Admin
from app.forms import (
    ComplaintForm, TrackComplaintForm, LoginForm, ComplaintStatusForm, BudgetForm,
)
from app.utils import generate_report_id, calculate_progress, COMPLAINT_STATUSES, is_safe_redirect_url

main_bp = Blueprint('main', __name__)
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Order matters: this is the sequence a healthy complaint moves through,
# and it drives the step tracker on the "Track Complaint" page.
STATUS_STEPS = ['Submitted', 'Under Review', 'In Progress', 'Resolved']


# ---------------------------------------------------------------------------
# Public-facing routes
# ---------------------------------------------------------------------------

@main_bp.route('/')
def home():
    """Landing page with a hero, quick stats, and links into the three
    main flows: submit a complaint, track a complaint, view the budget."""
    total_allocated = db.session.query(
        db.func.coalesce(db.func.sum(Budget.allocated_budget), 0)
    ).scalar()

    stats = {
        'total_complaints': Complaint.query.count(),
        'resolved_complaints': Complaint.query.filter_by(status='Resolved').count(),
        'total_projects': Budget.query.count(),
        'total_allocated': total_allocated,
    }
    return render_template('home.html', stats=stats)


@main_bp.route('/complaint/submit', methods=['GET', 'POST'])
def submit_complaint():
    """Citizen-facing complaint submission form."""
    form = ComplaintForm()

    if form.validate_on_submit():
        complaint = Complaint(
            report_id=generate_report_id(),
            category=form.category.data,
            description=form.description.data.strip(),
            location=form.location.data.strip() if form.location.data else None,
            citizen_name=form.citizen_name.data.strip() if form.citizen_name.data else None,
            phone_number=form.phone_number.data.strip() if form.phone_number.data else None,
            status='Submitted',
        )
        db.session.add(complaint)
        db.session.commit()

        flash('Complaint Submitted Successfully', 'success')
        return redirect(url_for('main.complaint_success', report_id=complaint.report_id))

    return render_template('submit_complaint.html', form=form)


@main_bp.route('/complaint/success/<report_id>')
def complaint_success(report_id):
    """Confirmation page shown right after a successful submission."""
    complaint = Complaint.query.filter_by(report_id=report_id).first()
    if complaint is None:
        abort(404)
    return render_template('complaint_success.html', complaint=complaint)


@main_bp.route('/complaint/receipt/<report_id>')
def complaint_receipt(report_id):
    """Minimal, printable receipt for a single complaint."""
    complaint = Complaint.query.filter_by(report_id=report_id).first()
    if complaint is None:
        abort(404)
    return render_template('complaint_receipt.html', complaint=complaint, now=datetime.utcnow())


@main_bp.route('/complaint/track', methods=['GET', 'POST'])
def track_complaint():
    """Let a citizen look up a complaint by Report ID."""
    form = TrackComplaintForm()
    complaint = None
    searched = False
    status_index = -1

    if form.validate_on_submit():
        searched = True
        lookup_id = form.report_id.data.strip().upper()
        complaint = Complaint.query.filter_by(report_id=lookup_id).first()
        if complaint and complaint.status in STATUS_STEPS:
            status_index = STATUS_STEPS.index(complaint.status)

    return render_template(
        'track_complaint.html',
        form=form,
        complaint=complaint,
        searched=searched,
        status_steps=STATUS_STEPS,
        status_index=status_index,
    )


@main_bp.route('/budget')
def budget():
    """Searchable, sortable, paginated table of county budget projects."""
    search = request.args.get('search', '', type=str).strip()
    sort = request.args.get('sort', 'project_name')
    direction = request.args.get('dir', 'asc')
    page = request.args.get('page', 1, type=int)

    query = Budget.query
    if search:
        like = f'%{search}%'
        query = query.filter(or_(
            Budget.project_name.ilike(like),
            Budget.ward.ilike(like),
            Budget.county.ilike(like),
            Budget.financial_year.ilike(like),
            Budget.project_status.ilike(like),
        ))

    sort_columns = {
        'project_name': Budget.project_name,
        'county': Budget.county,
        'financial_year': Budget.financial_year,
        'allocated_budget': Budget.allocated_budget,
        'progress_percentage': Budget.progress_percentage,
        'project_status': Budget.project_status,
    }
    column = sort_columns.get(sort, Budget.project_name)
    column = column.desc() if direction == 'desc' else column.asc()
    query = query.order_by(column)

    pagination = db.paginate(query, page=page, per_page=10, error_out=False)

    return render_template(
        'budget.html',
        pagination=pagination,
        projects=pagination.items,
        search=search,
        sort=sort,
        direction=direction,
    )


@main_bp.route('/budget/print')
def budget_print():
    """Printable version of the full budget report (ignores search/sort)."""
    projects = Budget.query.order_by(Budget.county, Budget.project_name).all()
    return render_template('budget_print.html', projects=projects, now=datetime.utcnow())


# ---------------------------------------------------------------------------
# Admin routes
# ---------------------------------------------------------------------------

@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('admin.dashboard'))

    form = LoginForm()
    if form.validate_on_submit():
        admin = Admin.query.filter_by(username=form.username.data.strip()).first()
        if admin and admin.check_password(form.password.data):
            login_user(admin)
            flash(f'Welcome back, {admin.username}!', 'success')
            next_page = request.args.get('next')
            if next_page and is_safe_redirect_url(next_page):
                return redirect(next_page)
            return redirect(url_for('admin.dashboard'))
        flash('Invalid username or password.', 'danger')

    return render_template('admin/login.html', form=form)


@admin_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('admin.login'))


@admin_bp.route('/dashboard')
@login_required
def dashboard():
    total_complaints = Complaint.query.count()
    pending_complaints = Complaint.query.filter(
        Complaint.status.in_(['Submitted', 'Under Review', 'In Progress'])
    ).count()
    resolved_complaints = Complaint.query.filter_by(status='Resolved').count()
    total_projects = Budget.query.count()

    status_counts = {
        status: Complaint.query.filter_by(status=status).count()
        for status in COMPLAINT_STATUSES
    }

    recent_complaints = (
        Complaint.query.order_by(Complaint.date_submitted.desc()).limit(5).all()
    )

    return render_template(
        'admin/dashboard.html',
        total_complaints=total_complaints,
        pending_complaints=pending_complaints,
        resolved_complaints=resolved_complaints,
        total_projects=total_projects,
        status_counts=status_counts,
        recent_complaints=recent_complaints,
    )


@admin_bp.route('/complaints')
@login_required
def complaints():
    search = request.args.get('search', '', type=str).strip()
    status_filter = request.args.get('status', '')
    page = request.args.get('page', 1, type=int)

    query = Complaint.query
    if search:
        like = f'%{search}%'
        query = query.filter(or_(
            Complaint.report_id.ilike(like),
            Complaint.category.ilike(like),
            Complaint.citizen_name.ilike(like),
            Complaint.location.ilike(like),
        ))
    if status_filter:
        query = query.filter_by(status=status_filter)

    query = query.order_by(Complaint.date_submitted.desc())
    pagination = db.paginate(query, page=page, per_page=10, error_out=False)
    status_form = ComplaintStatusForm()

    return render_template(
        'admin/complaints.html',
        pagination=pagination,
        complaints=pagination.items,
        search=search,
        status_filter=status_filter,
        statuses=COMPLAINT_STATUSES,
        status_form=status_form,
    )


@admin_bp.route('/complaints/<int:complaint_id>/update', methods=['POST'])
@login_required
def update_complaint_status(complaint_id):
    complaint = db.session.get(Complaint, complaint_id)
    if complaint is None:
        abort(404)

    form = ComplaintStatusForm()
    if form.validate_on_submit():
        complaint.status = form.status.data
        db.session.commit()
        flash(f'Complaint {complaint.report_id} updated to "{complaint.status}".', 'success')
    else:
        flash('Could not update complaint status. Please try again.', 'danger')

    return redirect(url_for('admin.complaints'))


@admin_bp.route('/complaints/<int:complaint_id>/delete', methods=['POST'])
@login_required
def delete_complaint(complaint_id):
    complaint = db.session.get(Complaint, complaint_id)
    if complaint is None:
        abort(404)

    report_id = complaint.report_id
    db.session.delete(complaint)
    db.session.commit()
    flash(f'Complaint {report_id} deleted.', 'info')
    return redirect(url_for('admin.complaints'))


@admin_bp.route('/complaints/export')
@login_required
def export_complaints():
    """Export every complaint as a downloadable CSV file."""
    complaints_list = Complaint.query.order_by(Complaint.date_submitted.desc()).all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        'Report ID', 'Category', 'Description', 'Location', 'Citizen Name',
        'Phone Number', 'Date Submitted', 'Status',
    ])
    for c in complaints_list:
        writer.writerow([
            c.report_id, c.category, c.description, c.location or '',
            c.citizen_name or '', c.phone_number or '',
            c.date_submitted.strftime('%Y-%m-%d %H:%M'), c.status,
        ])

    response = Response(output.getvalue(), mimetype='text/csv')
    response.headers['Content-Disposition'] = (
        f'attachment; filename=complaints_export_{datetime.utcnow().strftime("%Y%m%d")}.csv'
    )
    return response


@admin_bp.route('/budget')
@login_required
def budget_list():
    projects = Budget.query.order_by(Budget.county, Budget.project_name).all()
    return render_template('admin/budget_list.html', projects=projects)


@admin_bp.route('/budget/add', methods=['GET', 'POST'])
@login_required
def add_budget():
    form = BudgetForm()
    if form.validate_on_submit():
        progress = calculate_progress(form.allocated_budget.data, form.amount_spent.data)
        project = Budget(
            project_name=form.project_name.data.strip(),
            ward=form.ward.data.strip(),
            county=form.county.data,
            financial_year=form.financial_year.data.strip(),
            allocated_budget=form.allocated_budget.data,
            amount_spent=form.amount_spent.data,
            progress_percentage=progress,
            project_status=form.project_status.data,
        )
        db.session.add(project)
        db.session.commit()
        flash(f'Project "{project.project_name}" added.', 'success')
        return redirect(url_for('admin.budget_list'))

    return render_template('admin/budget_form.html', form=form, mode='add')


@admin_bp.route('/budget/<int:project_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_budget(project_id):
    project = db.session.get(Budget, project_id)
    if project is None:
        abort(404)

    form = BudgetForm(obj=project)
    if form.validate_on_submit():
        form.populate_obj(project)
        project.progress_percentage = calculate_progress(project.allocated_budget, project.amount_spent)
        db.session.commit()
        flash(f'Project "{project.project_name}" updated.', 'success')
        return redirect(url_for('admin.budget_list'))

    return render_template('admin/budget_form.html', form=form, mode='edit', project=project)


@admin_bp.route('/budget/<int:project_id>/delete', methods=['POST'])
@login_required
def delete_budget(project_id):
    project = db.session.get(Budget, project_id)
    if project is None:
        abort(404)

    name = project.project_name
    db.session.delete(project)
    db.session.commit()
    flash(f'Project "{name}" deleted.', 'info')
    return redirect(url_for('admin.budget_list'))

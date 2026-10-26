/**
 * College Maintenance and Request System - Role-Based Web Controller
 * Course Code: 24CS305 / CS3106 - DBMS Laboratory
 * Strict Role-Based Access Control (RBAC):
 * - Technician: Selects and logs materials required; executes work and resolves issues.
 * - Admin: Allocates technicians and views materials used (view-only for materials, no selection access).
 * - Faculty & Student: Dedicated complaint reporting & personal ticket status tracking.
 */

// Global State
let currentUser = null;
let metadata = { departments: [], categories: [], technicians: [], inventory: [] };
let allRequests = [];
let selectedWfRequestId = null;
let categoryChartInstance = null;
let techFilterOnlyMe = true;

// Role Labels for Gateway
const ROLE_LABELS = {
    student_faculty: 'Student / Faculty',
    technician: 'Technician',
    admin: 'Administrator'
};

document.addEventListener('DOMContentLoaded', async () => {
    setupTabNavigation();
    setupEventListeners();
    await checkInitialSession();
    await loadMetadata();
});

// Toast Notifications
function showToast(message, type = 'success') {
    const container = document.getElementById('toast-container');
    if (!container) return;
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    const icon = type === 'success' ? 'fa-check-circle' : 'fa-exclamation-circle';
    toast.innerHTML = `<i class="fas ${icon}"></i> <span>${message}</span>`;
    container.appendChild(toast);
    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(100%)';
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

// Session Initialization
async function checkInitialSession() {
    try {
        const res = await fetch('/api/auth/current_user');
        const data = await res.json();
        if (data.authenticated && data.user) {
            currentUser = data.user;
            showPortalForRole(currentUser);
        } else {
            showLoginGateway();
        }
    } catch (e) {
        showLoginGateway();
    }
}

function showLoginGateway() {
    document.getElementById('login-gateway').style.display = 'flex';
    document.getElementById('main-app-portal').style.display = 'none';
    selectGatewayRole('student_faculty');
}

function selectGatewayRole(roleKey) {
    document.querySelectorAll('.role-select-card').forEach(card => card.classList.remove('active'));
    const targetCard = document.querySelector(`.role-select-card[data-role="${roleKey}"]`);
    if (targetCard) targetCard.classList.add('active');

    const label = ROLE_LABELS[roleKey] || 'Student / Faculty';
    const userField = document.getElementById('gateway-username');
    const passField = document.getElementById('gateway-password');
    if (userField) userField.value = '';
    if (passField) passField.value = '';

    const submitBtn = document.getElementById('gateway-submit-btn');
    if (submitBtn) {
        submitBtn.innerHTML = `<i class="fas fa-arrow-right-to-bracket"></i> Sign In to Portal`;
    }

    const desc = document.getElementById('gateway-active-role-desc');
    if (desc) {
        desc.textContent = `Signing in as ${label}`;
    }
}

function fillCredential(username, password, label) {
    // Disabled: manual login only
}

async function handleGatewayLogin(event) {
    event.preventDefault();
    const u = document.getElementById('gateway-username').value.trim();
    const p = document.getElementById('gateway-password').value.trim();

    if (!u || !p) {
        showToast('Please enter both username and password.', 'error');
        return;
    }

    try {
        const res = await fetch('/api/auth/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username: u, password: p })
        });
        const data = await res.json();
        if (data.success) {
            currentUser = data.user;
            showToast(`Welcome, ${currentUser.full_name}! Signed in as ${currentUser.role}`);
            showPortalForRole(currentUser);
        } else {
            showToast(data.message || 'Login failed', 'error');
        }
    } catch (e) {
        showToast('Server communication error', 'error');
    }
}

async function handleLogout() {
    try {
        await fetch('/api/auth/logout', { method: 'POST' });
        currentUser = null;
        showToast('Logged out successfully.');
        showLoginGateway();
    } catch (e) {
        showLoginGateway();
    }
}

// Show Portal for User Role
function showPortalForRole(user) {
    document.getElementById('login-gateway').style.display = 'none';
    document.getElementById('main-app-portal').style.display = 'flex';

    // Set body CSS role class for strict CSS visibility
    const role = user.role;
    if (role === 'Admin') {
        document.body.className = 'role-admin';
    } else if (role === 'Technician') {
        document.body.className = 'role-technician';
    } else {
        document.body.className = 'role-reporter';
    }

    // Render User Badge in Topbar
    const rolePillClass = role.toLowerCase() === 'admin' ? 'admin' : (role.toLowerCase() === 'technician' ? 'technician' : 'student');
    document.getElementById('topbar-user-badge').innerHTML = `
        <i class="fas fa-user-circle" style="font-size:1.1rem; color:var(--primary);"></i>
        <span>${escapeHtml(user.full_name)}</span>
        <span class="role-pill ${rolePillClass}">${user.role}</span>
        <span style="color:var(--text-muted); font-size:0.75rem;">(${escapeHtml(user.dept_name)})</span>
    `;

    if (role === 'Student' || role === 'Staff') {
        // STUDENTS & FACULTY: Single unified complaints interface
        document.getElementById('requests-page-title').textContent = 'My Reported Issues';
        document.getElementById('requests-page-desc').textContent = 'Live tracking of complaints submitted by your account';
        const newTicketLabel = document.getElementById('btn-new-ticket-label');
        if (newTicketLabel) newTicketLabel.textContent = 'Report Issue';
        
        switchTab('requests-tab');

    } else if (role === 'Technician') {
        // TECHNICIAN:
        document.getElementById('workflow-page-title').textContent = 'Technician Workbench';
        document.getElementById('wf-list-header-title').innerHTML = '<i class="fas fa-list-check text-primary"></i> My Assigned Tasks';

        // Load technician profile bar and workbench stats
        loadTechnicianProfile();
        switchTab('workflow-tab');

    } else {
        // ADMIN:
        document.getElementById('requests-page-title').textContent = 'All Campus Maintenance Requests';
        document.getElementById('requests-page-desc').textContent = 'Search, filter, update, assign, and manage all campus maintenance complaints';
        const newTicketLabel = document.getElementById('btn-new-ticket-label');
        if (newTicketLabel) newTicketLabel.textContent = 'New Maintenance Ticket';
        document.getElementById('workflow-page-title').textContent = 'Technician Allocation & Materials Auditing';
        document.getElementById('wf-list-header-title').innerHTML = '<i class="fas fa-list-check text-primary"></i> Campus Maintenance Jobs';

        switchTab('dashboard-tab');
    }
}

// Load Technician Profile & Stats
async function loadTechnicianProfile() {
    if (!currentUser || currentUser.role !== 'Technician') return;
    try {
        const res = await fetch('/api/technician/profile');
        const data = await res.json();
        if (data.success) {
            const t = data.technician;
            const s = data.stats;
            document.getElementById('tech-profile-name').textContent = `${t.name} (Technician Workbench)`;
            document.getElementById('tech-profile-spec').textContent = t.specialization;
            document.getElementById('tech-profile-rate').textContent = `₹${parseFloat(t.hourly_rate).toFixed(2)}/hr`;

            document.getElementById('tech-stat-total').textContent = s.total_assigned || 0;
            document.getElementById('tech-stat-pending').textContent = s.pending_start || 0;
            document.getElementById('tech-stat-inprog').textContent = s.in_progress || 0;
            document.getElementById('tech-stat-completed').textContent = s.completed || 0;

            const badgeCount = document.getElementById('tech-badge-count');
            if (badgeCount) badgeCount.textContent = `${(s.pending_start || 0) + (s.in_progress || 0)} Active`;
        }
    } catch (e) {
        console.error('Error loading tech profile', e);
    }
}

// Tab Navigation
function setupTabNavigation() {
    const navItems = document.querySelectorAll('.nav-item');
    navItems.forEach(item => {
        item.addEventListener('click', () => {
            const tabId = item.getAttribute('data-tab');
            switchTab(tabId);
        });
    });
}

function switchTab(tabId) {
    document.querySelectorAll('.nav-item').forEach(btn => btn.classList.remove('active'));
    document.querySelectorAll('.tab-pane').forEach(pane => pane.classList.remove('active'));

    const activeBtn = document.querySelector(`.nav-item[data-tab="${tabId}"]`);
    const activePane = document.getElementById(tabId);
    if (activeBtn) activeBtn.classList.add('active');
    if (activePane) activePane.classList.add('active');

    // Trigger tab-specific refresh
    if (tabId === 'dashboard-tab') loadDashboard();
    if (tabId === 'requests-tab') loadRequests();
    if (tabId === 'workflow-tab') loadWorkflow();
    if (tabId === 'inventory-tab') loadInventory();
    if (tabId === 'reports-tab') loadReports();
    if (tabId === 'system-tab') loadSystemStatus();
}

function setupEventListeners() {
    const searchInput = document.getElementById('req-search');
    if (searchInput) {
        searchInput.addEventListener('input', () => filterAndRenderRequests());
    }

    document.getElementById('filter-status')?.addEventListener('change', () => filterAndRenderRequests());
    document.getElementById('filter-priority')?.addEventListener('change', () => filterAndRenderRequests());
    document.getElementById('filter-category')?.addEventListener('change', () => filterAndRenderRequests());

    document.getElementById('report-type-select')?.addEventListener('change', (e) => {
        loadReportData(e.target.value);
    });
}

// Metadata
async function loadMetadata() {
    try {
        const res = await fetch('/api/metadata');
        metadata = await res.json();
        populateFormDropdowns();
    } catch (e) {
        console.error('Error loading metadata', e);
    }
}

function populateFormDropdowns() {
    const modalCat = document.getElementById('new-req-category');
    const modalDept = document.getElementById('new-req-department');
    const filterCat = document.getElementById('filter-category');

    const catOptions = (metadata.categories || []).map(c => `<option value="${c.category_id}">${c.category_name} (SLA: ${c.sla_hours}h)</option>`).join('');
    const deptOptions = (metadata.departments || []).map(d => `<option value="${d.dept_id}">${d.dept_name} (${d.building})</option>`).join('');

    if (modalCat) modalCat.innerHTML = catOptions;
    if (modalDept) modalDept.innerHTML = deptOptions;

    if (filterCat) {
        filterCat.innerHTML = `<option value="All">All Categories</option>` + (metadata.categories || []).map(c => `<option value="${c.category_name}">${c.category_name}</option>`).join('');
    }

    const techSelect = document.getElementById('wf-tech-select');
    if (techSelect) {
        techSelect.innerHTML = (metadata.technicians || []).map(t => `<option value="${t.technician_id}">${t.name} (${t.specialization}) - Status: ${t.status}</option>`).join('');
    }

    const partSelect = document.getElementById('wf-part-select');
    if (partSelect) {
        partSelect.innerHTML = (metadata.inventory || []).map(p => `<option value="${p.part_id}">${p.part_name} [Stock: ${p.stock_quantity} ${p.unit_of_measure}] @ ₹${parseFloat(p.unit_cost).toFixed(2)}</option>`).join('');
        updateSelectedPartStock();
    }
}

function updateSelectedPartStock() {
    const partSelect = document.getElementById('wf-part-select');
    const stockBadge = document.getElementById('wf-stock-badge');
    const qtyInput = document.getElementById('wf-part-qty');
    if (!partSelect || !stockBadge) return;

    const selectedPartId = parseInt(partSelect.value);
    const part = (metadata.inventory || []).find(p => p.part_id === selectedPartId);
    if (part) {
        const stock = part.stock_quantity;
        if (stock <= 0) {
            stockBadge.className = 'badge badge-emergency';
            stockBadge.innerHTML = `<i class="fas fa-times-circle"></i> Out of Stock (0 ${part.unit_of_measure})`;
            if (qtyInput) qtyInput.max = 0;
        } else if (stock <= part.reorder_level) {
            stockBadge.className = 'badge badge-high';
            stockBadge.innerHTML = `<i class="fas fa-exclamation-triangle"></i> Low Stock: ${stock} ${part.unit_of_measure}`;
            if (qtyInput) qtyInput.max = stock;
        } else {
            stockBadge.className = 'badge badge-low';
            stockBadge.innerHTML = `<i class="fas fa-check-circle"></i> In Stock: ${stock} ${part.unit_of_measure}`;
            if (qtyInput) qtyInput.max = stock;
        }
    }
}

// ============================================================================
// DASHBOARD CONTROLLER (ADMIN ONLY)
// ============================================================================

function filterRequestsByDashboard(status) {
    switchTab('requests-tab');
    const filterStatus = document.getElementById('filter-status');
    if (filterStatus) {
        filterStatus.value = status;
        filterAndRenderRequests();
    }
}

async function loadDashboard() {
    if (!currentUser || currentUser.role !== 'Admin') return;
    try {
        const res = await fetch('/api/dashboard');
        const data = await res.json();
        if (!data.success) return;

        document.getElementById('stat-total-requests').textContent = data.stats.total_requests || 0;
        document.getElementById('stat-pending').textContent = data.stats.pending || 0;
        document.getElementById('stat-in-progress').textContent = data.stats.in_progress || 0;
        document.getElementById('stat-resolved').textContent = data.stats.resolved || 0;
        document.getElementById('stat-techs').textContent = data.stats.available_techs || 0;
        document.getElementById('stat-cost').textContent = `₹${(data.stats.total_parts_cost || 0).toLocaleString('en-IN', {minimumFractionDigits: 2})}`;

        const urgentBody = document.getElementById('dashboard-urgent-table');
        if (urgentBody) {
            if (data.urgent_requests.length === 0) {
                urgentBody.innerHTML = `<tr><td colspan="4" style="text-align: center; color: var(--text-muted); padding: 1.5rem;">✅ No urgent unattended complaints!</td></tr>`;
            } else {
                urgentBody.innerHTML = data.urgent_requests.map(r => `
                    <tr style="cursor:pointer;" onclick="viewRequestDetails(${r.request_id})">
                        <td><span class="tracking-code">${r.tracking_code}</span></td>
                        <td><strong>${escapeHtml(r.issue_title)}</strong><br><small style="color:var(--text-muted);">${escapeHtml(r.location_details)}</small></td>
                        <td><span class="badge ${getPriorityBadgeClass(r.priority)}">${r.priority}</span></td>
                        <td><span class="badge badge-status ${getStatusBadgeClass(r.status)}">${r.status}</span></td>
                    </tr>
                `).join('');
            }
        }

        const alertBox = document.getElementById('dashboard-stock-alert');
        if (alertBox) {
            if (data.low_stock_parts.length > 0) {
                alertBox.style.display = 'block';
                alertBox.style.cursor = 'pointer';
                alertBox.innerHTML = `⚠️ <strong>Inventory Alert:</strong> ${data.low_stock_parts.length} part(s) at or below reorder threshold (${data.low_stock_parts.map(p => p.part_name).join(', ')}). <u>Click to open Inventory</u>`;
            } else {
                alertBox.style.display = 'none';
            }
        }

        renderCategoryChart(data.categories);
    } catch (e) {
        console.error('Error loading dashboard', e);
    }
}

function renderCategoryChart(categories) {
    const canvas = document.getElementById('categoryDoughnutChart');
    if (!canvas) return;

    const labels = categories.map(c => c.category_name);
    const counts = categories.map(c => c.total_requests);

    if (categoryChartInstance) categoryChartInstance.destroy();

    categoryChartInstance = new Chart(canvas, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: counts,
                backgroundColor: ['#3b82f6', '#10b981', '#f59e0b', '#8b5cf6', '#ec4899', '#06b6d4'],
                borderWidth: 2,
                borderColor: '#ffffff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: 'bottom', labels: { font: { family: 'Plus Jakarta Sans', size: 11 }, boxWidth: 12 } }
            },
            cutout: '70%'
        }
    });
}

// ============================================================================
// REQUESTS CONTROLLER
// ============================================================================
async function loadRequests() {
    try {
        const res = await fetch('/api/requests');
        const data = await res.json();
        allRequests = data.requests || [];
        filterAndRenderRequests();
    } catch (e) {
        console.error('Error loading requests', e);
    }
}

function filterAndRenderRequests() {
    const search = document.getElementById('req-search')?.value.toLowerCase().trim() || '';
    const status = document.getElementById('filter-status')?.value || 'All';
    const priority = document.getElementById('filter-priority')?.value || 'All';
    const category = document.getElementById('filter-category')?.value || 'All';

    const filtered = allRequests.filter(r => {
        const matchSearch = !search || 
            r.tracking_code.toLowerCase().includes(search) ||
            r.issue_title.toLowerCase().includes(search) ||
            r.location_details.toLowerCase().includes(search) ||
            r.reported_by.toLowerCase().includes(search);

        const matchStatus = (status === 'All') || (r.status === status);
        const matchPriority = (priority === 'All') || (r.priority === priority);
        const matchCategory = (category === 'All') || (r.category_name === category);

        return matchSearch && matchStatus && matchPriority && matchCategory;
    });

    renderRequestsTable(filtered);
}

function renderRequestsTable(requests) {
    const tbody = document.getElementById('requests-table-body');
    const countBadge = document.getElementById('request-total-count');
    if (countBadge) countBadge.textContent = `${requests.length} records`;

    if (!tbody) return;

    if (requests.length === 0) {
        tbody.innerHTML = `<tr><td colspan="9" style="text-align: center; color: var(--text-muted); padding: 2.5rem;">No maintenance requests found.</td></tr>`;
        return;
    }

    const isAdmin = currentUser && currentUser.role === 'Admin';
    const isTech = currentUser && currentUser.role === 'Technician';

    tbody.innerHTML = requests.map(r => `
        <tr>
            <td><span class="tracking-code">${r.tracking_code}</span></td>
            <td>
                <strong>${escapeHtml(r.issue_title)}</strong>
                <div style="font-size: 0.75rem; color: var(--text-muted); margin-top: 2px;">
                    <i class="fas fa-map-marker-alt"></i> ${escapeHtml(r.location_details)} (${escapeHtml(r.dept_name)})
                </div>
            </td>
            <td><span style="font-weight: 600; font-size: 0.82rem; color: var(--secondary);">${escapeHtml(r.category_name)}</span></td>
            <td><span class="badge ${getPriorityBadgeClass(r.priority)}">${r.priority}</span></td>
            <td><span class="badge badge-status ${getStatusBadgeClass(r.status)}">${r.status}</span></td>
            <td><span style="font-size: 0.82rem;">${escapeHtml(r.reported_by)}</span></td>
            <td><span style="font-size: 0.82rem; font-weight: 500;">${r.technician_name ? escapeHtml(r.technician_name) : '<em style="color:var(--text-muted)">Unassigned</em>'}</span></td>
            <td style="font-size: 0.78rem; color: var(--text-muted);">${formatDate(r.reported_at)}</td>
            <td>
                <div class="action-btn-group">
                    <button class="btn-icon" title="View Ticket Status" onclick="viewRequestDetails(${r.request_id})">
                        <i class="fas fa-eye"></i>
                    </button>
                    ${isAdmin ? `
                    <button class="btn-icon" title="Edit Request" onclick="openEditModal(${r.request_id})">
                        <i class="fas fa-pen"></i>
                    </button>
                    <button class="btn-icon delete" title="Delete Request" onclick="deleteRequest(${r.request_id}, '${r.tracking_code}')">
                        <i class="fas fa-trash-alt"></i>
                    </button>` : ''}
                </div>
            </td>
        </tr>
    `).join('');
}

// Modal: Issue Reporting (Used by Student, Faculty, Admin)
function openNewRequestModal() {
    document.getElementById('new-req-form')?.reset();
    populateFormDropdowns();
    document.getElementById('modal-new-request').classList.add('active');
}

function closeNewRequestModal() {
    document.getElementById('modal-new-request').classList.remove('active');
}

async function submitNewRequest(event) {
    event.preventDefault();
    const title = document.getElementById('new-req-title').value.trim();
    const catId = document.getElementById('new-req-category').value;
    const deptId = document.getElementById('new-req-department').value;
    const loc = document.getElementById('new-req-location').value.trim();
    const pri = document.getElementById('new-req-priority').value;
    const desc = document.getElementById('new-req-desc').value.trim();

    if (!title || !loc || !desc) {
        showToast('Please fill all required fields.', 'error');
        return;
    }

    try {
        const res = await fetch('/api/requests', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                issue_title: title,
                category_id: catId,
                dept_id: deptId,
                location_details: loc,
                priority: pri,
                issue_description: desc
            })
        });
        const data = await res.json();
        if (data.success) {
            showToast(`Complaint registered successfully! Tracking Code: ${data.tracking_code}`);
            closeNewRequestModal();
            loadRequests();
            if (currentUser && currentUser.role === 'Admin') loadDashboard();
        } else {
            showToast(data.message || 'Error logging request', 'error');
        }
    } catch (e) {
        showToast('Server error logging request', 'error');
    }
}

// Modal: View Request Details
async function viewRequestDetails(reqId) {
    try {
        const res = await fetch(`/api/requests/${reqId}`);
        const data = await res.json();
        if (!data.success) {
            showToast(data.message || 'Error loading details', 'error');
            return;
        }

        const r = data.request;
        const isStaffOrStudent = currentUser && (currentUser.role === 'Student' || currentUser.role === 'Staff');

        document.getElementById('view-req-code').textContent = r.tracking_code;
        document.getElementById('view-req-title').textContent = r.issue_title;
        document.getElementById('view-req-status-badge').className = `badge badge-status ${getStatusBadgeClass(r.status)}`;
        document.getElementById('view-req-status-badge').textContent = r.status;
        document.getElementById('view-req-pri-badge').className = `badge ${getPriorityBadgeClass(r.priority)}`;
        document.getElementById('view-req-pri-badge').textContent = r.priority;

        document.getElementById('view-req-dept').textContent = `${r.dept_name} (${r.building})`;
        document.getElementById('view-req-location').textContent = r.location_details;
        document.getElementById('view-req-reported-by').textContent = `${r.reported_by}`;
        document.getElementById('view-req-date').textContent = formatDate(r.reported_at);
        document.getElementById('view-req-desc').textContent = r.issue_description;

        const resBox = document.getElementById('view-req-res-box');
        if (r.resolution_notes) {
            resBox.style.display = 'block';
            document.getElementById('view-req-res-notes').textContent = r.resolution_notes;
            document.getElementById('view-req-resolved-at').textContent = formatDate(r.resolved_at);
        } else {
            resBox.style.display = 'none';
        }

        const partsContainer = document.getElementById('view-req-parts-section');
        if (isStaffOrStudent) {
            partsContainer.style.display = 'none';
        } else {
            partsContainer.style.display = 'block';
            const partsTbody = document.getElementById('view-req-parts-body');
            let totalCost = 0;
            if ((data.parts_used || []).length === 0) {
                partsTbody.innerHTML = `<tr><td colspan="4" style="text-align: center; color: var(--text-muted); padding: 1rem;">No replacement parts recorded yet.</td></tr>`;
            } else {
                partsTbody.innerHTML = data.parts_used.map(p => {
                    totalCost += parseFloat(p.total_cost);
                    return `
                        <tr>
                            <td><strong>${escapeHtml(p.part_name)}</strong></td>
                            <td>${p.quantity_used} ${p.unit_of_measure}</td>
                            <td>₹${parseFloat(p.unit_cost_charged).toFixed(2)}</td>
                            <td><strong>₹${parseFloat(p.total_cost).toFixed(2)}</strong></td>
                        </tr>
                    `;
                }).join('');
            }
            document.getElementById('view-req-total-cost').textContent = `₹${totalCost.toLocaleString('en-IN', {minimumFractionDigits: 2})}`;
        }

        document.getElementById('modal-view-details').classList.add('active');
    } catch (e) {
        showToast('Error loading ticket info', 'error');
    }
}

function closeViewDetailsModal() {
    document.getElementById('modal-view-details').classList.remove('active');
}

// Modal: Edit Request (Admin)
async function openEditModal(reqId) {
    try {
        const res = await fetch(`/api/requests/${reqId}`);
        const data = await res.json();
        const r = data.request;

        document.getElementById('edit-req-id').value = r.request_id;
        document.getElementById('edit-req-code').textContent = r.tracking_code;
        document.getElementById('edit-req-title').value = r.issue_title;
        document.getElementById('edit-req-priority').value = r.priority;
        document.getElementById('edit-req-status').value = r.status;
        document.getElementById('edit-req-location').value = r.location_details;
        document.getElementById('edit-req-desc').value = r.issue_description;

        const catSelect = document.getElementById('edit-req-category');
        catSelect.innerHTML = (metadata.categories || []).map(c => `<option value="${c.category_id}" ${c.category_id === r.category_id ? 'selected' : ''}>${c.category_name}</option>`).join('');

        const deptSelect = document.getElementById('edit-req-department');
        deptSelect.innerHTML = (metadata.departments || []).map(d => `<option value="${d.dept_id}" ${d.dept_id === r.dept_id ? 'selected' : ''}>${d.dept_name}</option>`).join('');

        document.getElementById('modal-edit-request').classList.add('active');
    } catch (e) {
        showToast('Error opening edit modal', 'error');
    }
}

function closeEditModal() {
    document.getElementById('modal-edit-request').classList.remove('active');
}

async function submitEditRequest(event) {
    event.preventDefault();
    const reqId = document.getElementById('edit-req-id').value;
    const title = document.getElementById('edit-req-title').value.trim();
    const catId = document.getElementById('edit-req-category').value;
    const deptId = document.getElementById('edit-req-department').value;
    const loc = document.getElementById('edit-req-location').value.trim();
    const pri = document.getElementById('edit-req-priority').value;
    const status = document.getElementById('edit-req-status').value;
    const desc = document.getElementById('edit-req-desc').value.trim();

    try {
        const res = await fetch(`/api/requests/${reqId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                issue_title: title,
                category_id: catId,
                dept_id: deptId,
                location_details: loc,
                priority: pri,
                status: status,
                issue_description: desc
            })
        });
        const data = await res.json();
        if (data.success) {
            showToast('Request updated successfully');
            closeEditModal();
            loadRequests();
            if (currentUser && currentUser.role === 'Admin') loadDashboard();
        } else {
            showToast(data.message || 'Update failed', 'error');
        }
    } catch (e) {
        showToast('Server update error', 'error');
    }
}

// Delete Request
async function deleteRequest(reqId, code) {
    if (!confirm(`Delete ticket ${code}? All assignment and materials data will be permanently removed.`)) return;

    try {
        const res = await fetch(`/api/requests/${reqId}`, { method: 'DELETE' });
        const data = await res.json();
        if (data.success) {
            showToast(`Ticket ${code} deleted.`);
            loadRequests();
            if (currentUser && currentUser.role === 'Admin') loadDashboard();
        } else {
            showToast(data.message || 'Delete failed', 'error');
        }
    } catch (e) {
        showToast('Server error on delete', 'error');
    }
}

// ============================================================================
// WORKFLOW & TECHNICIAN WORKBENCH CONTROLLER
// ============================================================================

async function loadWorkflow() {
    try {
        const res = await fetch('/api/requests');
        const data = await res.json();
        allRequests = data.requests || [];
        renderWorkflowJobsList();

        if (currentUser && currentUser.role === 'Technician') {
            loadTechnicianProfile();
        }
    } catch (e) {
        console.error('Error loading workflow', e);
    }
}

function renderWorkflowJobsList() {
    const selectList = document.getElementById('wf-request-selector-list');
    if (!selectList) return;

    let displayList = allRequests;
    // Strict RBAC: If Technician, ONLY show jobs assigned to this technician
    if (currentUser && currentUser.role === 'Technician') {
        const myTechId = currentUser.technician_id || 1;
        displayList = allRequests.filter(r => r.assigned_technician_id === myTechId);
    }

    if (displayList.length === 0) {
        selectList.innerHTML = `<div style="text-align:center; padding:2rem; color:var(--text-muted); font-size:0.88rem;">No active maintenance jobs found.</div>`;
        return;
    }

    selectList.innerHTML = displayList.map(r => `
        <div class="wf-selector-item ${selectedWfRequestId === r.request_id ? 'active' : ''}" onclick="selectWfRequest(${r.request_id})" id="wf-item-${r.request_id}">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 4px;">
                <span class="tracking-code">${r.tracking_code}</span>
                <span class="badge badge-status ${getStatusBadgeClass(r.status)}">${r.status}</span>
            </div>
            <div style="font-weight:700; font-size:0.85rem; color:var(--text-primary);">${escapeHtml(r.issue_title)}</div>
            <div style="font-size:0.75rem; color:var(--text-muted); margin-top:2px;">
                <i class="fas fa-map-marker-alt"></i> ${escapeHtml(r.location_details)}
            </div>
            <div style="font-size:0.75rem; color:var(--secondary); font-weight:600; margin-top:2px;">
                <i class="fas fa-wrench"></i> ${r.technician_name ? r.technician_name : 'No tech assigned'}
            </div>
        </div>
    `).join('');

    // If none selected, auto-select first
    if (displayList.length > 0 && (!selectedWfRequestId || !displayList.find(r => r.request_id === selectedWfRequestId))) {
        selectWfRequest(displayList[0].request_id);
    }
}

async function selectWfRequest(reqId) {
    selectedWfRequestId = reqId;
    document.querySelectorAll('.wf-selector-item').forEach(el => el.classList.remove('active'));
    document.getElementById(`wf-item-${reqId}`)?.classList.add('active');

    const reqObj = allRequests.find(r => r.request_id === reqId);
    if (!reqObj) return;

    // Render concise banner
    document.getElementById('wf-selected-banner').innerHTML = `
        <div style="display:flex; justify-content:space-between; align-items:flex-start;">
            <div>
                <span class="tracking-code">${reqObj.tracking_code}</span>
                <strong style="font-size:0.95rem; margin-left:6px;">${escapeHtml(reqObj.issue_title)}</strong>
                <div style="font-size:0.8rem; color:var(--text-muted); margin-top:3px;">
                    <i class="fas fa-map-marker-alt"></i> ${escapeHtml(reqObj.location_details)} (${escapeHtml(reqObj.dept_name)})
                </div>
            </div>
            <div style="text-align:right;">
                <span class="badge ${getPriorityBadgeClass(reqObj.priority)}">${reqObj.priority}</span>
                <span class="badge badge-status ${getStatusBadgeClass(reqObj.status)}">${reqObj.status}</span>
            </div>
        </div>
        <div style="margin-top:6px; font-size:0.8rem; color:var(--text-secondary); background:rgba(0,0,0,0.03); padding:6px 10px; border-radius:var(--radius-sm);">
            <strong>Reported Issue:</strong> ${escapeHtml(reqObj.issue_description)}
        </div>
    `;

    // Dynamic visibility of action blocks based on Status
    const startBlock = document.getElementById('wf-start-work-block');
    const materialsBlock = document.getElementById('wf-materials-select-block');
    const resolveBlock = document.getElementById('wf-resolve-block');
    const resolvedBanner = document.getElementById('wf-resolved-banner');

    const isTech = currentUser && currentUser.role === 'Technician';
    const isAdmin = currentUser && currentUser.role === 'Admin';

    if (reqObj.status === 'Assigned') {
        if (startBlock) startBlock.style.display = 'block';
        if (materialsBlock) materialsBlock.style.display = isTech ? 'block' : 'none';
        if (resolveBlock) resolveBlock.style.display = 'none';
        if (resolvedBanner) resolvedBanner.style.display = 'none';
    } else if (reqObj.status === 'In-Progress') {
        if (startBlock) startBlock.style.display = 'none';
        if (materialsBlock) materialsBlock.style.display = isTech ? 'block' : 'none';
        if (resolveBlock) resolveBlock.style.display = 'block';
        if (resolvedBanner) resolvedBanner.style.display = 'none';
    } else if (reqObj.status === 'Resolved' || reqObj.status === 'Closed') {
        if (startBlock) startBlock.style.display = 'none';
        if (materialsBlock) materialsBlock.style.display = 'none';
        if (resolveBlock) resolveBlock.style.display = 'none';
        if (resolvedBanner) {
            resolvedBanner.style.display = 'block';
            document.getElementById('wf-resolved-notes-text').textContent = reqObj.resolution_notes ? `Notes: ${reqObj.resolution_notes}` : 'Completed successfully.';
        }
    } else {
        // Reported or other status
        if (startBlock) startBlock.style.display = 'block';
        if (materialsBlock) materialsBlock.style.display = 'none';
        if (resolveBlock) resolveBlock.style.display = 'none';
        if (resolvedBanner) resolvedBanner.style.display = 'none';
    }

    // Live fetch and render materials consumed for this request
    await loadWfPartsConsumed(reqId);
}

// Live table of materials consumed for selected request
async function loadWfPartsConsumed(reqId) {
    const tbody = document.getElementById('wf-parts-live-tbody');
    if (!tbody) return;

    try {
        const res = await fetch(`/api/requests/${reqId}`);
        const data = await res.json();
        const parts = data.parts_used || [];
        const isTech = currentUser && currentUser.role === 'Technician';
        const colSpan = isTech ? 5 : 4;

        if (parts.length === 0) {
            tbody.innerHTML = `<tr><td colspan="${colSpan}" style="text-align:center; color:var(--text-muted); padding:0.8rem;">No materials recorded yet for this job.</td></tr>`;
            return;
        }

        let total = 0;
        tbody.innerHTML = parts.map(p => {
            total += parseFloat(p.total_cost);
            return `
                <tr>
                    <td><strong>${escapeHtml(p.part_name)}</strong></td>
                    <td>${p.quantity_used} ${p.unit_of_measure}</td>
                    <td>₹${parseFloat(p.unit_cost_charged).toFixed(2)}</td>
                    <td><strong>₹${parseFloat(p.total_cost).toFixed(2)}</strong></td>
                    ${isTech ? `
                    <td style="text-align:center;">
                        <button class="btn-icon delete" title="Remove recorded material" onclick="executeDeletePartUsage(${p.usage_id})">
                            <i class="fas fa-trash-can"></i>
                        </button>
                    </td>` : ''}
                </tr>
            `;
        }).join('') + `
            <tr style="background:#f8fafc; font-weight:700;">
                <td colspan="${isTech ? 3 : 3}" style="text-align:right;">Total Material Cost:</td>
                <td style="color:var(--primary);">₹${total.toFixed(2)}</td>
                ${isTech ? '<td></td>' : ''}
            </tr>
        `;
    } catch (e) {
        tbody.innerHTML = `<tr><td colspan="5" style="text-align:center; color:var(--danger); padding:0.8rem;">Failed to load materials.</td></tr>`;
    }
}

// Admin assigns technician
async function executeAssignTechnician() {
    if (!selectedWfRequestId) {
        showToast('Please select a request from the left list', 'error');
        return;
    }
    const techId = document.getElementById('wf-tech-select').value;
    try {
        const res = await fetch('/api/workflow/assign', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ request_id: selectedWfRequestId, technician_id: techId })
        });
        const data = await res.json();
        if (data.success) {
            showToast('Technician assigned via Stored Procedure sp_assign_technician!');
            await loadWorkflow();
            await loadRequests();
            if (currentUser && currentUser.role === 'Admin') loadDashboard();
        } else {
            showToast(data.message, 'error');
        }
    } catch (e) {
        showToast('Stored procedure error', 'error');
    }
}

// Start Work
async function executeStartWork() {
    if (!selectedWfRequestId) {
        showToast('Please select a request first', 'error');
        return;
    }
    const notes = document.getElementById('wf-start-notes').value.trim();
    try {
        const res = await fetch('/api/workflow/start', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ request_id: selectedWfRequestId, work_notes: notes })
        });
        const data = await res.json();
        if (data.success) {
            showToast('Work started via Stored Procedure sp_start_maintenance_work!');
            await loadWorkflow();
            await loadRequests();
            if (currentUser && currentUser.role === 'Admin') loadDashboard();
            if (currentUser && currentUser.role === 'Technician') loadTechnicianProfile();
        } else {
            showToast(data.message, 'error');
        }
    } catch (e) {
        showToast('Procedure error', 'error');
    }
}

// Consume Part (Technician Action Only)
async function executeConsumePart() {
    if (!selectedWfRequestId) {
        showToast('Please select a request first', 'error');
        return;
    }
    const partId = document.getElementById('wf-part-select').value;
    const qty = document.getElementById('wf-part-qty').value;
    const notes = document.getElementById('wf-part-notes').value.trim();

    try {
        const res = await fetch('/api/workflow/consume_part', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ request_id: selectedWfRequestId, part_id: partId, quantity: qty, notes: notes })
        });
        const data = await res.json();
        if (data.success) {
            showToast('Material recorded! Inventory stock decremented via trigger.');
            document.getElementById('wf-part-notes').value = '';
            document.getElementById('wf-part-qty').value = '1';
            await loadWfPartsConsumed(selectedWfRequestId);
            await loadMetadata();
            if (currentUser && currentUser.role === 'Admin') loadDashboard();
        } else {
            showToast(data.message, 'error');
        }
    } catch (e) {
        showToast('Trigger execution error', 'error');
    }
}

// Remove Recorded Material (Technician Action Only)
async function executeDeletePartUsage(usageId) {
    if (!confirm('Remove this material record? Inventory stock will be restored automatically via database trigger.')) return;

    try {
        const res = await fetch(`/api/workflow/consume_part/${usageId}`, {
            method: 'DELETE'
        });
        const data = await res.json();
        if (data.success) {
            showToast('Material removed and inventory stock restored!');
            if (selectedWfRequestId) await loadWfPartsConsumed(selectedWfRequestId);
            await loadMetadata();
            if (currentUser && currentUser.role === 'Admin') loadDashboard();
        } else {
            showToast(data.message, 'error');
        }
    } catch (e) {
        showToast('Error removing material', 'error');
    }
}

// Resolve Request
async function executeResolveRequest() {
    if (!selectedWfRequestId) {
        showToast('Please select a request first', 'error');
        return;
    }
    const notes = document.getElementById('wf-resolve-notes').value.trim();
    try {
        const res = await fetch('/api/workflow/resolve', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ request_id: selectedWfRequestId, resolution_notes: notes })
        });
        const data = await res.json();
        if (data.success) {
            showToast('Ticket marked resolved via sp_resolve_maintenance_request!');
            await loadWorkflow();
            await loadRequests();
            if (currentUser && currentUser.role === 'Admin') loadDashboard();
            if (currentUser && currentUser.role === 'Technician') loadTechnicianProfile();
        } else {
            showToast(data.message, 'error');
        }
    } catch (e) {
        showToast('Procedure error', 'error');
    }
}

// ============================================================================
// INVENTORY CONTROLLER
// ============================================================================
async function loadInventory() {
    if (!currentUser || (currentUser.role !== 'Admin' && currentUser.role !== 'Technician')) return;
    try {
        const res = await fetch('/api/inventory');
        const data = await res.json();
        const tbody = document.getElementById('inventory-table-body');
        if (!tbody) return;

        const isAdmin = currentUser.role === 'Admin';

        tbody.innerHTML = (data.parts || []).map(p => {
            const isLow = p.stock_quantity <= p.reorder_level;
            return `
                <tr>
                    <td><span style="font-family:'JetBrains Mono'; font-weight:600;">#${p.part_id}</span></td>
                    <td><strong>${escapeHtml(p.part_name)}</strong></td>
                    <td><span style="color:var(--secondary); font-weight:600;">${escapeHtml(p.category)}</span></td>
                    <td>${p.unit_of_measure}</td>
                    <td>₹${parseFloat(p.unit_cost).toFixed(2)}</td>
                    <td><strong style="color: ${isLow ? 'var(--danger)' : 'var(--text-primary)'};">${p.stock_quantity}</strong></td>
                    <td>${p.reorder_level}</td>
                    <td>
                        <span class="badge ${isLow ? 'badge-emergency' : 'badge-low'}">
                            ${isLow ? '<i class="fas fa-exclamation-triangle"></i> Reorder' : '<i class="fas fa-check"></i> In Stock'}
                        </span>
                    </td>
                    <td>
                        ${isAdmin ? `
                        <button class="btn btn-secondary btn-sm" onclick="promptAdjustStock(${p.part_id}, '${escapeHtml(p.part_name)}', ${p.stock_quantity})">
                            <i class="fas fa-sliders-h"></i> Adjust Stock
                        </button>` : `<span style="color:var(--text-muted); font-size:0.75rem;">View Only</span>`}
                    </td>
                </tr>
            `;
        }).join('');
    } catch (e) {
        console.error('Error loading inventory', e);
    }
}

async function promptAdjustStock(partId, partName, currStock) {
    const newQty = prompt(`Enter new physical stock quantity for "${partName}":`, currStock);
    if (newQty === null) return;
    const qtyInt = parseInt(newQty);
    if (isNaN(qtyInt) || qtyInt < 0) {
        showToast('Please enter a valid non-negative integer', 'error');
        return;
    }

    try {
        const res = await fetch(`/api/inventory/${partId}/stock`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ stock_quantity: qtyInt })
        });
        const data = await res.json();
        if (data.success) {
            showToast('Stock quantity updated');
            loadInventory();
            if (currentUser && currentUser.role === 'Admin') loadDashboard();
        } else {
            showToast(data.message, 'error');
        }
    } catch (e) {
        showToast('Server update error', 'error');
    }
}

function openAddPartModal() {
    document.getElementById('new-part-form')?.reset();
    document.getElementById('modal-add-part').classList.add('active');
}
function closeAddPartModal() {
    document.getElementById('modal-add-part').classList.remove('active');
}
async function submitNewPart(event) {
    event.preventDefault();
    const name = document.getElementById('part-name').value.trim();
    const category = document.getElementById('part-category').value;
    const uom = document.getElementById('part-uom').value.trim();
    const cost = document.getElementById('part-cost').value;
    const stock = document.getElementById('part-stock').value;
    const reorder = document.getElementById('part-reorder').value;

    try {
        const res = await fetch('/api/inventory', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                part_name: name,
                category: category,
                unit_of_measure: uom,
                unit_cost: cost,
                stock_quantity: stock,
                reorder_level: reorder
            })
        });
        const data = await res.json();
        if (data.success) {
            showToast('New part cataloged in inventory!');
            closeAddPartModal();
            loadInventory();
            loadMetadata();
        } else {
            showToast(data.message, 'error');
        }
    } catch (e) {
        showToast('Server error adding part', 'error');
    }
}

// ============================================================================
// REPORTS & VIEWS CONTROLLER (ADMIN ONLY)
// ============================================================================
async function loadReports() {
    if (!currentUser || currentUser.role !== 'Admin') return;
    const reportType = document.getElementById('report-type-select')?.value || 'technician_workload';
    await loadReportData(reportType);
}

async function loadReportData(reportType) {
    try {
        const res = await fetch(`/api/reports/${reportType}`);
        const result = await res.json();
        if (!result.success) return;

        document.getElementById('report-sql-display').textContent = result.sql;
        const thead = document.getElementById('report-table-head');
        const tbody = document.getElementById('report-table-body');

        if (reportType === 'technician_workload') {
            thead.innerHTML = `<tr><th>Tech ID</th><th>Technician Name</th><th>Specialization</th><th>Status</th><th>Total Assigned</th><th>Pending</th><th>In-Progress</th><th>Completed</th></tr>`;
            tbody.innerHTML = (result.data || []).map(r => `
                <tr>
                    <td>#${r.technician_id}</td>
                    <td><strong>${escapeHtml(r.technician_name)}</strong></td>
                    <td>${escapeHtml(r.specialization)}</td>
                    <td><span class="badge ${r.current_status === 'Available' ? 'badge-low' : 'badge-high'}">${r.current_status}</span></td>
                    <td><strong>${r.total_assigned_tasks}</strong></td>
                    <td>${r.pending_tasks || 0}</td>
                    <td>${r.in_progress_tasks || 0}</td>
                    <td><strong style="color:var(--success);">${r.completed_tasks || 0}</strong></td>
                </tr>
            `).join('');
        } else if (reportType === 'request_cost_summary') {
            thead.innerHTML = `<tr><th>Tracking Code</th><th>Issue Title</th><th>Category</th><th>Status</th><th>Parts Types</th><th>Units Consumed</th><th>Total Material Expense</th></tr>`;
            tbody.innerHTML = (result.data || []).map(r => `
                <tr>
                    <td><span class="tracking-code">${r.tracking_code}</span></td>
                    <td><strong>${escapeHtml(r.issue_title)}</strong></td>
                    <td>${escapeHtml(r.category_name)}</td>
                    <td><span class="badge badge-status ${getStatusBadgeClass(r.status)}">${r.status}</span></td>
                    <td>${r.parts_count}</td>
                    <td>${r.total_items_consumed}</td>
                    <td><strong style="color:var(--primary);">₹${parseFloat(r.total_parts_cost).toLocaleString('en-IN', {minimumFractionDigits: 2})}</strong></td>
                </tr>
            `).join('');
        } else if (reportType === 'department_expenditure') {
            thead.innerHTML = `<tr><th>Department</th><th>Campus Building</th><th>Total Requests Lodged</th><th>Total Materials Expense</th></tr>`;
            tbody.innerHTML = (result.data || []).map(r => `
                <tr>
                    <td><strong>${escapeHtml(r.dept_name)}</strong></td>
                    <td>${escapeHtml(r.building)}</td>
                    <td>${r.request_count}</td>
                    <td><strong style="color:var(--primary);">₹${parseFloat(r.total_cost).toLocaleString('en-IN', {minimumFractionDigits: 2})}</strong></td>
                </tr>
            `).join('');
        } else if (reportType === 'category_distribution') {
            thead.innerHTML = `<tr><th>Category Name</th><th>Total Requests</th><th>Resolved Count</th><th>Open Count</th><th>Target SLA</th></tr>`;
            tbody.innerHTML = (result.data || []).map(r => `
                <tr>
                    <td><strong>${escapeHtml(r.category_name)}</strong></td>
                    <td>${r.total_requests}</td>
                    <td><strong style="color:var(--success);">${r.resolved_count}</strong></td>
                    <td>${r.open_count}</td>
                    <td>${r.sla_hours} hours</td>
                </tr>
            `).join('');
        }
    } catch (e) {
        console.error('Error fetching report', e);
    }
}

// ============================================================================
// SYSTEM STATUS CONTROLLER (ADMIN ONLY)
// ============================================================================
async function loadSystemStatus() {
    if (!currentUser || currentUser.role !== 'Admin') return;
    try {
        const res = await fetch('/api/system/status');
        const data = await res.json();
        if (!data.connected) return;

        document.getElementById('sys-status-pill').innerHTML = `<span class="badge" style="background:#ecfdf5; color:#047857;"><i class="fas fa-check-circle"></i> Connected to MySQL</span>`;
        document.getElementById('sys-server-info').textContent = data.server_info;
        document.getElementById('sys-db-name').textContent = data.config.database;
        document.getElementById('sys-db-host').textContent = `${data.config.host}:${data.config.port}`;
        document.getElementById('sys-db-user').textContent = data.config.user;

        const tbody = document.getElementById('sys-tables-body');
        if (tbody) {
            tbody.innerHTML = (data.tables || []).map(t => `
                <tr>
                    <td><strong>${t.name}</strong></td>
                    <td><span class="badge ${t.type === 'view' ? 'badge-high' : 'badge-medium'}">${t.type.toUpperCase()}</span></td>
                    <td><strong>${t.count}</strong> rows</td>
                </tr>
            `).join('');
        }
    } catch (e) {
        console.error('Error loading system status', e);
    }
}

// Helpers
function getPriorityBadgeClass(priority) {
    switch (priority) {
        case 'Emergency': return 'badge-emergency';
        case 'High': return 'badge-high';
        case 'Medium': return 'badge-medium';
        default: return 'badge-low';
    }
}

function getStatusBadgeClass(status) {
    switch (status) {
        case 'Reported': return 'status-reported';
        case 'Categorized': return 'status-categorized';
        case 'Assigned': return 'status-assigned';
        case 'In-Progress': return 'status-in-progress';
        case 'Resolved': return 'status-resolved';
        case 'Closed': return 'status-closed';
        default: return 'status-reported';
    }
}

function formatDate(dateStr) {
    if (!dateStr) return '-';
    try {
        const d = new Date(dateStr);
        return d.toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' });
    } catch (e) {
        return dateStr;
    }
}

function escapeHtml(text) {
    if (!text) return '';
    return text.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

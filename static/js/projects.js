(() => {
    const config = window.projectApiConfig;
    const searchForm = document.getElementById('project-search-form');
    const searchInput = document.getElementById('project-search-input');
    const loading = document.getElementById('projects-loading');
    const error = document.getElementById('projects-error');
    const empty = document.getElementById('projects-empty');
    const grid = document.getElementById('projects-grid');
    const projectForm = document.getElementById('project-form');
    const modal = document.getElementById('project-modal');
    const placeholderId = '00000000-0000-0000-0000-000000000000';
    let debounceTimer;
    let activeRequest;
    let editingId = null;

    const detailUrl = (id) => config.detailTemplate.replace(placeholderId, encodeURIComponent(id));
    const starUrl = (id) => config.starTemplate.replace(placeholderId, encodeURIComponent(id));

    function showState(state) {
        loading.classList.toggle('hide', state !== 'loading');
        error.classList.toggle('hide', state !== 'error');
        empty.classList.toggle('hide', state !== 'empty');
        grid.classList.toggle('hide', state !== 'grid');
    }

    function makeTextElement(tag, className, text) {
        const element = document.createElement(tag);
        if (className) element.className = className;
        element.textContent = text || '';
        return element;
    }

    function makeProjectCard(project) {
        const card = document.createElement('article');
        card.className = 'experience-card';
        card.append(makeTextElement('span', 'experience-category', project.tech_stack));
        card.append(makeTextElement('h2', '', project.title));
        card.append(makeTextElement('p', 'experience-description', project.description));

        if (project.project_image_url) {
            const image = document.createElement('img');
            image.src = project.project_image_url;
            image.alt = `Preview ${project.title}`;
            image.loading = 'lazy';
            image.referrerPolicy = 'no-referrer';
            image.className = 'project-image';
            image.addEventListener('error', () => image.remove(), { once: true });
            card.append(image);
        }

        const actions = document.createElement('div');
        actions.className = 'skills-actions';
        if (project.project_url) {
            const link = makeTextElement('a', 'button', 'Lihat proyek');
            link.href = project.project_url;
            link.target = '_blank';
            link.rel = 'noopener noreferrer';
            actions.append(link);
        }

        const starButton = makeTextElement(
            'button', `button button-star${project.is_starred ? ' is-starred' : ''}`,
            `${project.is_starred ? 'Unstar' : 'Star'} ${project.star_count}`,
        );
        starButton.type = 'button';
        starButton.title = project.starred_by_names
            ? `Dibintangi oleh ${project.starred_by_names}`
            : 'Jadilah yang pertama memberi star';
        starButton.addEventListener('click', () => toggleStar(project.id, starButton));
        actions.append(starButton);

        if (config.canManage) {
            const editButton = makeTextElement('button', 'button button-secondary', 'Edit');
            editButton.type = 'button';
            editButton.addEventListener('click', () => openEdit(project));
            const deleteButton = makeTextElement('button', 'button button-danger', 'Hapus');
            deleteButton.type = 'button';
            deleteButton.addEventListener('click', () => deleteProject(project.id, deleteButton));
            actions.append(editButton, deleteButton);
        }
        card.append(actions);
        return card;
    }

    async function loadProjects(query = '') {
        if (activeRequest) activeRequest.abort();
        activeRequest = new AbortController();
        showState('loading');
        const url = new URL(config.listUrl, window.location.origin);
        if (query) url.searchParams.set('title', query);
        try {
            const response = await fetch(url, {
                headers: { Accept: 'application/json' },
                signal: activeRequest.signal,
            });
            if (!response.ok) throw new Error(`Request failed (${response.status})`);
            const projects = await response.json();
            grid.replaceChildren();
            if (!projects.length) {
                showState('empty');
                return;
            }
            projects.forEach((project) => grid.append(makeProjectCard(project)));
            showState('grid');
        } catch (requestError) {
            if (requestError.name === 'AbortError') return;
            console.error('Error loading projects:', requestError);
            showState('error');
        }
    }

    function csrfToken() {
        return document.querySelector('#api-csrf-form [name=csrfmiddlewaretoken]')?.value || '';
    }

    async function sendJson(url, method, body) {
        const headers = { Accept: 'application/json', 'X-CSRFToken': csrfToken() };
        if (body) headers['Content-Type'] = 'application/json';
        return fetch(url, {
            method,
            headers,
            credentials: 'same-origin',
            body: body ? JSON.stringify(body) : undefined,
        });
    }

    async function toggleStar(id, button) {
        button.disabled = true;
        try {
            const response = await sendJson(starUrl(id), 'POST');
            if (!response.ok) throw new Error(response.status === 403 ? 'Silakan login untuk memberi star.' : 'Gagal mengubah star.');
            await loadProjects(searchInput.value.trim());
        } catch (requestError) {
            showToast('Gagal', requestError.message, 'error');
        } finally {
            button.disabled = false;
        }
    }

    function openEdit(project) {
        editingId = project.id;
        document.getElementById('project-modal-title').textContent = 'Edit Project';
        for (const key of ['title', 'description', 'tech_stack', 'project_url', 'project_image_url']) {
            const field = projectForm.elements.namedItem(key);
            if (field) field.value = project[key] || '';
        }
        modal.showPopover();
    }

    function showFormErrors(data) {
        projectForm.querySelectorAll('[data-field-error]').forEach((node) => {
            node.textContent = '';
            node.classList.add('hide');
        });
        Object.entries(data).forEach(([field, messages]) => {
            const node = projectForm.querySelector(`[data-field-error="${CSS.escape(field)}"]`);
            if (node) {
                node.textContent = Array.isArray(messages) ? messages.map((item) => item.message || item).join(' ') : String(messages);
                node.classList.remove('hide');
            }
        });
    }

    if (projectForm) {
        projectForm.addEventListener('submit', async (event) => {
            event.preventDefault();
            const submitButton = projectForm.querySelector('[type=submit]');
            submitButton.disabled = true;
            showFormErrors({});
            const payload = Object.fromEntries(new FormData(projectForm).entries());
            delete payload.csrfmiddlewaretoken;
            try {
                const response = await sendJson(editingId ? detailUrl(editingId) : config.listUrl, editingId ? 'PATCH' : 'POST', payload);
                const data = await response.json().catch(() => ({}));
                if (!response.ok) {
                    showFormErrors(data);
                    const message = Object.values(data).flat().map((item) => item.message || item).join(' ');
                    throw new Error(message || `Terjadi kesalahan (status ${response.status}).`);
                }
                projectForm.reset();
                editingId = null;
                modal.hidePopover();
                showToast('Berhasil', 'Project berhasil disimpan.', 'success');
                await loadProjects(searchInput.value.trim());
            } catch (requestError) {
                showToast('Gagal menyimpan project', requestError.message, 'error');
            } finally {
                submitButton.disabled = false;
            }
        });

        modal?.addEventListener('toggle', (event) => {
            if (event.newState === 'closed') {
                editingId = null;
                projectForm.reset();
                document.getElementById('project-modal-title').textContent = 'Tambah Project';
                showFormErrors({});
            }
        });
    }

    async function deleteProject(id, button) {
        if (!window.confirm('Yakin ingin menghapus project ini?')) return;
        button.disabled = true;
        try {
            const response = await sendJson(detailUrl(id), 'DELETE');
            if (!response.ok) throw new Error(`Gagal menghapus project (status ${response.status}).`);
            showToast('Berhasil', 'Project berhasil dihapus.', 'success');
            await loadProjects(searchInput.value.trim());
        } catch (requestError) {
            showToast('Gagal', requestError.message, 'error');
            button.disabled = false;
        }
    }

    searchInput.addEventListener('input', () => {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(() => loadProjects(searchInput.value.trim()), 300);
    });
    searchForm.addEventListener('submit', (event) => {
        event.preventDefault();
        clearTimeout(debounceTimer);
        loadProjects(searchInput.value.trim());
    });
    document.querySelector('[popovertarget="project-modal"]')?.addEventListener('click', () => {
        editingId = null;
        projectForm?.reset();
        const title = document.getElementById('project-modal-title');
        if (title) title.textContent = 'Tambah Project';
    });

    loadProjects(searchInput.value.trim());
})();

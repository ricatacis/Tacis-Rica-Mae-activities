document.getElementById('subject-select').addEventListener('change', function() {
    const subjectId = this.value;
    if (subjectId) {
        // Load grades for the selected subject
        loadGradesForSubject(subjectId);
    } else {
        // Clear the grades table
        document.querySelector('#grades-table tbody').innerHTML = '';
    }
});

function loadGradesForSubject(subjectId) {
    fetch(`/api/grades?subject_id=${subjectId}`)
        .then(response => response.json())
        .then(grades => {
            const tbody = document.querySelector('#grades-table tbody');
            tbody.innerHTML = '';
            
            grades.forEach(grade => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${grade.student_id}</td>
                    <td>${grade.student_name}</td>
                    <td>${grade.value}</td>
                    <td>
                        <button class="edit-btn" data-id="${grade.id}">Edit</button>
                        <button class="delete-btn" data-id="${grade.id}">Delete</button>
                    </td>
                `;
                tbody.appendChild(row);
            });
        });
}
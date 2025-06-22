// Confirm before deleting a task
document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('a[data-delete]').forEach(function (deleteLink) {
        deleteLink.addEventListener('click', function (event) {
            if (!confirm('Are you sure you want to delete this task?')) {
                event.preventDefault();
            }
        });
    });
});

let dashboardButtons = document.querySelectorAll('button.update-btn');
let updaateStatusForms = document.querySelectorAll('form.update-status-form');

dashboardButtons.forEach((button, index) => {
    button.addEventListener('click', () => {
        let updateForm = updaateStatusForms[index]; // Match the corresponding form
        if (updateForm.classList.contains('hide')) {
            updateForm.classList.remove('hide');
            button.innerHTML = 'Cancel';
            button.style.backgroundColor = '#D22626';
        } else {
            updateForm.classList.add('hide');
            button.innerHTML = 'Update Status';
            button.style.backgroundColor = '#D22626';
        }
    });
});

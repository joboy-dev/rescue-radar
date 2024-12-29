let dashboardButtons = document.querySelectorAll('button.edit');
let reassignForms = document.querySelectorAll('form.reassign-form');

dashboardButtons.forEach((button, index) => {
    button.addEventListener('click', () => {
        let reassignForm = reassignForms[index]; // Match the corresponding form
        if (reassignForm.classList.contains('hide')) {
            reassignForm.classList.remove('hide');
            button.innerHTML = 'Cancel';
            button.style.backgroundColor = '#D22626';
        } else {
            reassignForm.classList.add('hide');
            button.innerHTML = 'Assign';
            button.style.backgroundColor = '#FC924B';
        }
    });
});

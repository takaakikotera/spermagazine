document.addEventListener('DOMContentLoaded', function() {
    var choices = document.querySelectorAll('.choice-label');
    choices.forEach(function(choice) {
        choice.addEventListener('click', function() {
            choices.forEach(function(c) {
                c.style.backgroundColor = '';
            });
            choice.style.backgroundColor = '#d0d0d0';
        });
    });
});
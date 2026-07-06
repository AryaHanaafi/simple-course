document.addEventListener('DOMContentLoaded', () => {
    // Confirmation popup for actions
    const confirmButtons = document.querySelectorAll('.confirm-action');
    confirmButtons.forEach(btn => {
        btn.addEventListener('click', (e) => {
            const message = btn.getAttribute('data-confirm') || 'Are you sure you want to perform this action?';
            if (!confirm(message)) {
                e.preventDefault();
            }
        });
    });

    // Quiz AJAX Submission
    const quizForm = document.getElementById('quiz-form');
    if (quizForm) {
        quizForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const bankId = quizForm.getAttribute('data-bank-id');
            const submitUrl = `/student-space/quiz/${bankId}/submit/`;
            
            // Collect answers
            const formData = new FormData(quizForm);
            const answers = {};
            for (let [key, value] of formData.entries()) {
                if (key.startsWith('question_')) {
                    const qId = key.split('_')[1];
                    answers[qId] = value;
                }
            }

            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

            fetch(submitUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify({ answers: answers })
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    const resultDiv = document.getElementById('quiz-result');
                    resultDiv.innerHTML = `<div class="card" style="border-color: var(--success)">
                        <h3 style="color: var(--success)">Quiz Completed!</h3>
                        <p>Score: <strong>${data.score}%</strong></p>
                        <p>Correct Answers: ${data.correct_count}</p>
                    </div>`;
                    quizForm.style.display = 'none'; // Hide form after submission
                } else {
                    alert('Error submitting quiz: ' + data.message);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('An error occurred while submitting the quiz.');
            });
        });
    }
});

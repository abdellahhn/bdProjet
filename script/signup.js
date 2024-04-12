  document.getElementById('signup-form').addEventListener('submit', function(event) {
    event.preventDefault();
    const formData = new FormData(this);
    const userData = {};
    formData.forEach((value, key) => {
        userData[key] = value;
    });

    fetch('/signup', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(userData)
    })
    .then(response => response.json())
    .then(data => {
        console.log(data);
    })
    .catch(error => {
        console.error('Error:', error);
    });
});

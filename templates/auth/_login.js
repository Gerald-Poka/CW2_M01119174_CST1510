
document.addEventListener('DOMContentLoaded', function () {
			var form = document.getElementById('login-form');
			if (!form) return;

			var username = document.getElementById('username');
			var password = document.getElementById('password');

			function setInvalid(input, message) {
				input.classList.toggle('is-invalid', !!message);
				var error = document.getElementById(input.id + '-error');
				if (error) {
					error.textContent = message || '';
					error.style.display = message ? 'block' : 'none';
				}
			}

			function clearInvalid(input) {
				setInvalid(input, '');
			}

			[username, password].forEach(function (input) {
				input.addEventListener('input', function () {
					clearInvalid(input);
				});
			});

			form.addEventListener('submit', function (event) {
				var valid = true;

				if (!username.value.trim()) {
					setInvalid(username, 'Username is required.');
					valid = false;
				}
				if (!password.value) {
					setInvalid(password, 'Password is required.');
					valid = false;
				}

				if (!valid) {
					event.preventDefault();
				}
			});
		});

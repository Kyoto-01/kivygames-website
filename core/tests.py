from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


User = get_user_model()


class AuthenticationFlowTests(TestCase):
	def test_register_persists_user_and_logs_in(self):
		response = self.client.post(
			reverse('register'),
			{
				'username': 'nova_player',
				'email': 'nova@example.com',
				'password1': 'UmaSenhaForte123!',
				'password2': 'UmaSenhaForte123!',
			},
			follow=True,
		)

		self.assertRedirects(response, reverse('profile'))
		user = User.objects.get(username='nova_player')
		self.assertEqual(user.email, 'nova@example.com')
		self.assertTrue(user.check_password('UmaSenhaForte123!'))
		self.assertEqual(int(self.client.session['_auth_user_id']), user.pk)

	def test_register_rejects_duplicate_email(self):
		User.objects.create_user(username='existing', email='repeat@example.com', password='SenhaForte123!')

		response = self.client.post(
			reverse('register'),
			{
				'username': 'other_user',
				'email': 'repeat@example.com',
				'password1': 'OutraSenhaForte123!',
				'password2': 'OutraSenhaForte123!',
			},
		)

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'Este e-mail ja esta cadastrado.')
		self.assertEqual(User.objects.filter(email='repeat@example.com').count(), 1)

	def test_delete_account_removes_user_from_database(self):
		user = User.objects.create_user(
			username='delete_me',
			email='delete@example.com',
			password='SenhaForte123!',
		)
		self.client.login(username='delete_me', password='SenhaForte123!')

		response = self.client.post(reverse('delete_account'), {'password': 'SenhaForte123!'}, follow=True)

		self.assertRedirects(response, reverse('home'))
		self.assertFalse(User.objects.filter(pk=user.pk).exists())
		self.assertNotIn('_auth_user_id', self.client.session)

	def test_delete_account_with_wrong_password_keeps_user(self):
		user = User.objects.create_user(
			username='keep_me',
			email='keep@example.com',
			password='SenhaForte123!',
		)
		self.client.login(username='keep_me', password='SenhaForte123!')

		response = self.client.post(reverse('delete_account'), {'password': 'senha-errada'})

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'Senha incorreta. Confirme sua senha para excluir a conta.')
		self.assertTrue(User.objects.filter(pk=user.pk).exists())

self.addEventListener('push', function (event) {
  let data = {};
  try {
    data = event.data.json();
  } catch (e) {
    data = { title: 'Notification', body: 'You have a new message.' };
  }

  const title = data.title || 'New Notification';
  const options = {
    body: data.body || '',
    icon: '/assets/images/icon.png',
  };

  event.waitUntil(self.registration.showNotification(title, options));
});


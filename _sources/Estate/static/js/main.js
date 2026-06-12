document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.thumb').forEach((button) => {
    button.addEventListener('click', () => {
      const img = document.getElementById('mainGalleryImage');
      if (!img) return;
      img.src = button.dataset.img;
      document.querySelectorAll('.thumb').forEach((thumb) => thumb.classList.remove('active'));
      button.classList.add('active');
    });
  });

  setTimeout(() => {
    document.querySelectorAll('.toast-stack .alert').forEach((alert) => {
      alert.style.transition = 'opacity .4s, transform .4s';
      alert.style.opacity = '0';
      alert.style.transform = 'translateY(-8px)';
      setTimeout(() => alert.remove(), 450);
    });
  }, 4500);

  document.querySelectorAll('form[data-confirm]').forEach((form) => {
    form.addEventListener('submit', (event) => {
      if (!window.confirm(form.dataset.confirm)) event.preventDefault();
    });
  });
});

const buyButtons = document.querySelectorAll('.buy-btn');
buyButtons.forEach(function(button) {
  button.addEventListener('click', function(event) {
    const productDiv = event.target.closest('.product');
    const imageSrc = productDiv.querySelector('.product-image').src;
    const name = productDiv.querySelector('.p-name').getAttribute('data-name');
    const price = productDiv.querySelector('.p-price').getAttribute('data-price');
    window.location.href = '/sproduct?image=' + encodeURIComponent(imageSrc) + '&name=' + encodeURIComponent(name) + '&price=' + encodeURIComponent(price);
  });
});

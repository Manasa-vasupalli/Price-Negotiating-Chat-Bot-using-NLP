$(document).ready(function() {
  $('.add-to-cart-btn').click(function(event) {
    event.preventDefault();
    var name = $('input[name="name"]').val();
    var price = $('input[name="price"]').val();
    var image = $('input[name="image"]').val();
    var size = $('#size').val();
    var quantity = $('#quantity').val();

    var item = {
      // "product_id": generateProductId(image),
      "name": name,
      "price": price,
      "image": image,
      "size": size,
      "quantity": quantity
    };

    var cart = JSON.parse(localStorage.getItem('cart')) || [];
    cart.push(item);
    localStorage.setItem('cart', JSON.stringify(cart));

    // Create a new FormData object
    var formData = new FormData();
    // Append the form data to the FormData object
    formData.append('name', name);
    formData.append('price', price);
    formData.append('image', image);
    formData.append('size', size);
    formData.append('quantity', quantity);

    // Submit the form data using JavaScript
    fetch('/add-to-cart', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(item)
    }).then(function(response) {
      // Redirect the user to the cart page
      window.location.href = '/cart';
    }).catch(function(error) {
      console.error(error);
    });
  });
});





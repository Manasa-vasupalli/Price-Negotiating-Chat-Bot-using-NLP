$(document).ready(function() {
    $('.remove-from-cart-btn').click(function(event) {
        event.preventDefault();
        var productId = $(this).data('product-id');
        var cart = JSON.parse(localStorage.getItem('cart')) || [];
        var updatedCart = cart.filter(function(item) {
            return item.product_id !== productId;
        });
        localStorage.setItem('cart', JSON.stringify(updatedCart));
        $.ajax({
            url: '/remove-from-cart',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ product_id: productId }),
            success: function(response) {
                window.location.reload();
            },
            error: function(error) {
                console.error(error);
            }
        });
    });
});
